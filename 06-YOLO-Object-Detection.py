{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# YOLO v3 Object Detection\n",
    "\n",
    "Let's see how to use the state of the art in object detection! Please make sure to watch the video, there is no code along here, since we can't reasonably train the YOLOv3 network ourself, instead we will use a pre-established version.\n",
    "\n",
    "CODE SOURCE: https://github.com/xiaochus/YOLOv3\n",
    "\n",
    "REFERENCE (for original YOLOv3): \n",
    "\n",
    "        @article{YOLOv3,  \n",
    "              title={YOLOv3: An Incremental Improvement},  \n",
    "              author={J Redmon, A Farhadi },\n",
    "              year={2018} \n",
    "--------\n",
    "----------\n",
    "## YOU MUST WATCH THE VIDEO LECTURE TO PROPERLY SET UP THE MODEL AND WEIGHTS. THIS NOTEBOOK WON'T WORK UNLESS YOU FOLLOW THE EXACT SET UP SHOWN IN THE VIDEO LECTURE.\n",
    "-------\n",
    "-------"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 30,
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "import time\n",
    "import cv2\n",
    "import numpy as np\n",
    "from model.yolo_model import YOLO"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 31,
   "metadata": {},
   "outputs": [],
   "source": [
    "def process_image(img):\n",
    "    \"\"\"Resize, reduce and expand image.\n",
    "\n",
    "    # Argument:\n",
    "        img: original image.\n",
    "\n",
    "    # Returns\n",
    "        image: ndarray(64, 64, 3), processed image.\n",
    "    \"\"\"\n",
    "    image = cv2.resize(img, (416, 416),\n",
    "                       interpolation=cv2.INTER_CUBIC)\n",
    "    image = np.array(image, dtype='float32')\n",
    "    image /= 255.\n",
    "    image = np.expand_dims(image, axis=0)\n",
    "\n",
    "    return image"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 32,
   "metadata": {},
   "outputs": [],
   "source": [
    "def get_classes(file):\n",
    "    \"\"\"Get classes name.\n",
    "\n",
    "    # Argument:\n",
    "        file: classes name for database.\n",
    "\n",
    "    # Returns\n",
    "        class_names: List, classes name.\n",
    "\n",
    "    \"\"\"\n",
    "    with open(file) as f:\n",
    "        class_names = f.readlines()\n",
    "    class_names = [c.strip() for c in class_names]\n",
    "\n",
    "    return class_names"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 40,
   "metadata": {},
   "outputs": [],
   "source": [
    "def draw(image, boxes, scores, classes, all_classes):\n",
    "    \"\"\"Draw the boxes on the image.\n",
    "\n",
    "    # Argument:\n",
    "        image: original image.\n",
    "        boxes: ndarray, boxes of objects.\n",
    "        classes: ndarray, classes of objects.\n",
    "        scores: ndarray, scores of objects.\n",
    "        all_classes: all classes name.\n",
    "    \"\"\"\n",
    "    for box, score, cl in zip(boxes, scores, classes):\n",
    "        x, y, w, h = box\n",
    "\n",
    "        top = max(0, np.floor(x + 0.5).astype(int))\n",
    "        left = max(0, np.floor(y + 0.5).astype(int))\n",
    "        right = min(image.shape[1], np.floor(x + w + 0.5).astype(int))\n",
    "        bottom = min(image.shape[0], np.floor(y + h + 0.5).astype(int))\n",
    "\n",
    "        cv2.rectangle(image, (top, left), (right, bottom), (255, 0, 0), 2)\n",
    "        cv2.putText(image, '{0} {1:.2f}'.format(all_classes[cl], score),\n",
    "                    (top, left - 6),\n",
    "                    cv2.FONT_HERSHEY_SIMPLEX,\n",
    "                    5, (0, 255, 0), 1,\n",
    "                    cv2.LINE_AA)\n",
    "\n",
    "        print('class: {0}, score: {1:.2f}'.format(all_classes[cl], score))\n",
    "        print('box coordinate x,y,w,h: {0}'.format(box))\n",
    "\n",
    "    print()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 34,
   "metadata": {},
   "outputs": [],
   "source": [
    "def detect_image(image, yolo, all_classes):\n",
    "    \"\"\"Use yolo v3 to detect images.\n",
    "\n",
    "    # Argument:\n",
    "        image: original image.\n",
    "        yolo: YOLO, yolo model.\n",
    "        all_classes: all classes name.\n",
    "\n",
    "    # Returns:\n",
    "        image: processed image.\n",
    "    \"\"\"\n",
    "    pimage = process_image(image)\n",
    "\n",
    "    start = time.time()\n",
    "    boxes, classes, scores = yolo.predict(pimage, image.shape)\n",
    "    end = time.time()\n",
    "\n",
    "    print('time: {0:.2f}s'.format(end - start))\n",
    "\n",
    "    if boxes is not None:\n",
    "        draw(image, boxes, scores, classes, all_classes)\n",
    "\n",
    "    return image"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 35,
   "metadata": {},
   "outputs": [],
   "source": [
    "def detect_video(video, yolo, all_classes):\n",
    "    \"\"\"Use yolo v3 to detect video.\n",
    "\n",
    "    # Argument:\n",
    "        video: video file.\n",
    "        yolo: YOLO, yolo model.\n",
    "        all_classes: all classes name.\n",
    "    \"\"\"\n",
    "    video_path = os.path.join(\"videos\", \"test\", video)\n",
    "    camera = cv2.VideoCapture(video_path)\n",
    "    cv2.namedWindow(\"detection\", cv2.WINDOW_AUTOSIZE)\n",
    "\n",
    "    # Prepare for saving the detected video\n",
    "    sz = (int(camera.get(cv2.CAP_PROP_FRAME_WIDTH)),\n",
    "        int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT)))\n",
    "    fourcc = cv2.VideoWriter_fourcc(*'mpeg')\n",
    "\n",
    "    \n",
    "    vout = cv2.VideoWriter()\n",
    "    vout.open(os.path.join(\"videos\", \"res\", video), fourcc, 20, sz, True)\n",
    "\n",
    "    while True:\n",
    "        res, frame = camera.read()\n",
    "\n",
    "        if not res:\n",
    "            break\n",
    "\n",
    "        image = detect_image(frame, yolo, all_classes)\n",
    "        cv2.imshow(\"detection\", image)\n",
    "\n",
    "        # Save the video frame by frame\n",
    "        vout.write(image)\n",
    "\n",
    "        if cv2.waitKey(110) & 0xff == 27:\n",
    "                break\n",
    "\n",
    "    vout.release()\n",
    "    camera.release()\n",
    "    "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 36,
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "C:\\Users\\Omar\\Anaconda3\\envs\\python-cvcourse\\lib\\site-packages\\keras\\engine\\saving.py:269: UserWarning: No training configuration found in save file: the model was *not* compiled. Compile it manually.\n",
      "  warnings.warn('No training configuration found in save file: '\n"
     ]
    }
   ],
   "source": [
    "yolo = YOLO(0.3, 0.5)\n",
    "file = 'data/coco_classes.txt'\n",
    "all_classes = get_classes(file)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Detecting Images"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 41,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "time: 76.17s\n",
      "class: person, score: 0.37\n",
      "box coordinate x,y,w,h: [605.1595211  476.31277871  32.9219069   79.98926258]\n",
      "class: car, score: 0.99\n",
      "box coordinate x,y,w,h: [ -2.31289566 503.01233912 249.41672534 121.31110442]\n",
      "class: car, score: 0.54\n",
      "box coordinate x,y,w,h: [193.9545837  488.0392524  157.98968017  76.02561429]\n",
      "class: car, score: 0.47\n",
      "box coordinate x,y,w,h: [108.80652189 487.65757692 157.81814396  87.84636274]\n",
      "class: truck, score: 0.94\n",
      "box coordinate x,y,w,h: [374.9597317  423.97152388 253.71091157 106.11611214]\n",
      "\n"
     ]
    },
    {
     "data": {
      "text/plain": [
       "True"
      ]
     },
     "execution_count": 41,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "f = 'cars2.jpeg'\n",
    "path = 'images/'+f\n",
    "image = cv2.imread(path)\n",
    "image = detect_image(image, yolo, all_classes)\n",
    "cv2.imwrite('images/res/' + f, image)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Detecting on Video"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    " ##detect videos one at a time in videos/test folder    \n",
    " video = 'Bicycle Handlebar Camera (1).mp4'\n",
    " detect_video(video, yolo, all_classes)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.6.6"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
