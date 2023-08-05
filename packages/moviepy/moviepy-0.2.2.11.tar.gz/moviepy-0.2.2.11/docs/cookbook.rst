MoviePy's Cookbook
===================

Because short code examples can be better than a long doc, this page regroups
complete code snippets to give you an idea of what MoviePy can do and how you do it.


Reading and writing video files
--------------------------------


Audio operations
-----------------


Compositing video files
-------------------------

Adding text
------------

Common video transformations
-----------------------------

Resizing
~~~~~~~~~

clip.resize((400, 500))
clip.resize(width=300)
clip.resize(height=300)

clip.resize(lambda t: (300+t, 200+t)) # the clip gets larger with time
clip.resize(width = lambda t: 300+t) # the height will change to conserve ratio
clip.resize(height= lambda t: 300+t) # the height will change to conserve ratio

Cropping
~~~~~~~~~


Video FX
---------


accel_decel
~~~~~~~~~~~~

blackwhite
~~~~~~~~~~~~

blink
~~~~~~~~~~~~


colorx
~~~~~~~~~~~~

crop
~~~~~~~~~~~~

even_size
~~~~~~~~~~~~

fadein
~~~~~~~~~~~~

fadeout
~~~~~~~~~~~~

freeze
~~~~~~~~~~~~

freeze_region
~~~~~~~~~~~~

gamma_corr
~~~~~~~~~~~~

headblur
~~~~~~~~~~~~

invert_colors
~~~~~~~~~~~~

loop
~~~~~~~~~~~~

lum_contrast
~~~~~~~~~~~~

make_loopable
~~~~~~~~~~~~

margin
~~~~~~~~~~~~

mask_and
~~~~~~~~~~~~

mask_color
~~~~~~~~~~~~

mask_or
~~~~~~~~~~~~

mirror_x
~~~~~~~~~~~~

mirror_y
~~~~~~~~~~~~

painting
~~~~~~~~~~~~

rotation
~~~~~~~~~~~~

scroll
~~~~~~~~~~~~

speedx
~~~~~~~~~~~~

supersample
~~~~~~~~~~~~

time_mirror
~~~~~~~~~~~~

time_symmetrize
~~~~~~~~~~~~~~~~