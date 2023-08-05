:mod:`psychopy.visual` - many visual stimuli
==============================================================================

:class:`.Window` to display all stimuli below.


.. toctree::
    :hidden:
    :glob:

    visual/*

Commonly used:

	* :class:`.ImageStim` to show images
	* :class:`.TextStim` to show texts

Shapes (all special classes of :class:`ShapeStim`):

	* :class:`.ShapeStim` to draw shapes with arbitrary numbers of vertices
	* :class:`.Rect` to show rectangles
	* :class:`.Circle` to show circles
	* :class:`.Polygon` to show polygons
	* :class:`.Line` to show a line

Images and patterns:

	* :class:`.ImageStim` to show images
	* :class:`.SimpleImageStim` to show images without bells and whistles
	* :class:`.GratingStim` to show gratings
	* :class:`.RadialStim` to show annulus, a rotating wedge, a checkerboard etc

Multiple stimuli:

	* :class:`.ElementArrayStim` to show many stimuli of the same type
	* :class:`.DotStim` to show and control movement of dots

Other stimuli:

	* :class:`.MovieStim` to show movies
	* :class:`.RatingScale` to collect ratings
	* :class:`.CustomMouse` to change the cursor in windows with GUI. OBS: will be depricated soon

General purpose (applies to other stimuli):

	* :class:`.BufferImageStim` to make a faster-to-show "screenshot" of other stimuli
	* :class:`.Aperture` to restrict visibility area of other stimuli

See also :ref:`visualhelperfunctions`

