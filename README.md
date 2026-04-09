# 🎨 KineCanvas

So, I got tired of using a mouse to draw and wondered if I could just use my hands like some low-budget Iron Man. This is what happened. It's a Python tool that uses your webcam to track finger movements and turns them into actual drawings on the screen.

No fancy sensors needed—just a decent camera and a bit of math.

## 🕹️ How it works (The hand stuff)
It's all gesture-based. You don't have to touch your keyboard once the camera is on.

- **Drawing:** Just point your index finger up. Think of it like a laser pointer.
- **Oops, go back:** If you mess up, make a peace sign (✌️). That’s the eraser. It’s pretty precise—I designed it to "vacuum" up specific lines.
- **Rearranging:** Pinch your thumb and index (🤏) to grab a line and move it. Useful if you draw something cool but in the wrong spot.
- **Nuke it:** Wave your whole palm at the screen. It clears the whole canvas in one go.

## 🛠️ Setting it up
I'm running this on Python 3.12, but as long as you have 3.10 or higher, you're good.

First, grab the files:
`git clone https://github.com/Tusharxl/KineCanvas.git && cd KineCanvas`

Then you gotta install the libraries (OpenCV and MediaPipe mostly):
`pip install -r requirements.txt`

To start the app:
`python main.py`

## 📂 What are these files?
I didn't want one giant 500-line file, so I broke it up. 
* `main.py` does the heavy lifting with the webcam. 
* `config.py` is where you can mess with the colors or eraser size if you think my defaults suck. 
* `utils.py` is just the math behind the scenes—calculating distances so the app knows when you're actually pinching or just hovering.

If you find a bug or want to add a "rainbow mode" or something, feel free to mess with the code!
