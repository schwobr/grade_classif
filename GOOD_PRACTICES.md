# Good Practices for WSI data

This document is a list of good practices concerning Whole Slide Image data 
preprocessing. The goal is to have a check list to fill before starting a
deep learning project using this kind of data, hopefully avoiding common issues.

## Patch extraction

When working with WSI, we often need to extract patches as the original image
resolution is far too high to be processed using deep learning techniques.
Another solution could be to just downsample the original image but it would
remove a sizeable amount of information that one needs to make predictions based
on such images. Therefore patch extraction is almost always preferred. But how
many patches do we need to extract ? What size ? What level in the pyramid ?
While this mainly depends on the project, a few guidelines can still be used:

* The more the better. Whichever the chosen level, taking at least contiguous
  patches should be preferred, as it would allow us to then be picky with the
  patches we actually use. It also activates the possibility to perform
  segmentation based on the patches and scale it back to the whole image. Besides,
  deep learning always makes good use of more data.
* The level should match the level of precision needed. Often, different levels
  of context are needed to get a good enough understanding of a region. To
  accomplish that, we can extract patches at different levels and then create
  a model that takes full advantage of it. A good idea could be to stack images
  of from different levels such that the lowest level one is in the center of
  all the higher level ones.
* Another option is using bigger patches. Going from the lowest level needed, it
  is possible to acquire large patches, so that they both contain the necessary
  low-level information as well as some context to perform analysis.The
  drawback is that such large images can't be processed as big batches which can
  be detrimental to the optimization algorithm when it is based on SGD.