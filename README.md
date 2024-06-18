# D33Z-NU15-V2

libraries needed: pygame + numba

I reccomend running test.py, it's the most advanced version. 

This is just a demo of a renderer I made, its the most complex project i've ever made without using any tutorials.

"I originally wrote a big, in depth and detailed descrition of this project but my browser freaked out and deleted it without saving. Maybe I'll come back to it later, but I'm too annoyed to do it now" - annoyed me, a few months ago.

I personally call it a reverse-raycaster, as it uses math similar to a raycaster, but doesn't cast rays. 

For those of you who want to know how it works:
Everything that is rendered has is stored in memory as a 2D vector. You call it's draw method, and it does two things:
- takes the distance from it to the camera to decide what scale it should be.
- takes the angle between the camera and itself and compares it to the direction of the camera and it's field of view to decide where along the X axis it would be drawn on the screen
Once all the math has been done, it's appended to the RENDERLIST where everything is sorted by distance and drawn to the screen. I call it a reverse-raycaster as the projection method I use is just the function I use to transform a posiition on screen into a direction to cast a ray, but in reverse. You could also think of it as vertices casting rays to the camera instead of the camera casting rays. 

For those of you interested in the lore:
I chose to move away from casting rays as it gets significantly more complicated to cast rays into anything that isn't on a grid. I worked on my 3D project uding JavisX9's tutorial, and was introduced to the concept of rendering graphics by using vertices to interpolate what should be drawn where without having to do the same calculation for every angle that is visible. That reminded me of my old raycaster, and how casting a seperate ray for entities was extremely taxing, and had a significant amount of optimisation potential. I realised that an entity could be rendered by having it's position calculated with a single vertex, and simply scale and position a sprite to act as a billboard. I considered trying to migrate the whole engine to a true 3D renderer, but decided to stay with raycasting as I like the aestetic of old rendering techniques and migrating the engine would be way harder than just making a new one. 


 things to be improved: 
 The code comments are bad, typos everywhere, and looking back at the code there are many things that should have comments but don't
