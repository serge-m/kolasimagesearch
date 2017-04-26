## Kolasimagesearch
Image Search by descriptors. 

Based on elasticsearch and kolasimagestorage.

Very basic region extraction and descriptors are implemented. 
Images is split into left and right halves. 
Those are our ROIs. 
Color histograms are calculated for each ROI. 
Those are our descriptors.
L2 norm is used for similarity.

## References 
* [The complete guide to building an image search engine with Python and OpenCV](http://www.pyimagesearch.com/2014/12/01/complete-guide-building-image-search-engine-python-opencv/)
* [image-match](https://github.com/ascribe/image-match)

## Testing
* Install requirements from requirements.txt
* Install [kolasimagestorage](https://github.com/serge-m/kolasimagestorage)
* Run elastic search and image storage (required for integration tests)
 ```
 ./run_dependencies_for_tests.sh
 ```
 
* Run tests
 ```
 ./run_tests.sh
 ```

## Other

TODOs and Issues [here](https://github.com/serge-m/kolasimagesearch/issues)
