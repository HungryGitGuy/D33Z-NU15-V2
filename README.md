# Reverse-Raycaster

libraries needed: pygame + numba

I reccomend running test.py, it's the most advanced version. 

This is just a demo of a renderer I made. I personally call it a reverse-raycaster, as it uses math similar to a raycaster, but doesn't cast rays. 

Where a raycaster would take horizontal positions on the screen and convert them into angles to then cast rays in those directions to see what should be drawn in those locations, this takes that formula and uses it in reverse, allowing me to do a kind of screenspace projection in a 2-dimensional world.

For those of you interested in the lore:
I chose to move away from casting rays as it gets significantly more complicated to cast rays into anything that isn't on a grid, and higher resolution really takes a toll on performance. I worked on my 3D project uding JavisX9's tutorial, and got some intuition with rendering graphics by using vertices and interpolating what should be drawn between them. That reminded me of my old raycaster, and how casting a seperate ray for entities was a significant bottleneck. I realised that an entity could be rendered by having its position calculated with a single vertex, and simply scale and position a sprite to act as a billboard. I considered trying to migrate the whole engine to a true 3D renderer, but decided to stay with a raycaster-like architecture as I like the aestetic of old rendering techniques and migrating the engine would be way harder than just making a new one. 

 Before you jump in and look at the code yourself, keep in mind I wrote this project in 10th grade. There are many typos, the code is not clean at all, there are many things that should have comments but don't, and some of the comments that are there are not very helpful.
