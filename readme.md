
## Kolasimagesearch
Image Search by descriptors. 

Based on elasticsearch and kolasimagestorage.

## References 
* [The complete guide to building an image search engine with Python and OpenCV](http://www.pyimagesearch.com/2014/12/01/complete-guide-building-image-search-engine-python-opencv/)
* [image-match](https://github.com/ascribe/image-match)

## Testing
* Install requirements from requirements.txt
* Run elastic search and image storage using 
 ```
 ./run_dependencies_for_tests.sh
 ```
 (required for integraion tests)
* Run tests
 ```
 ./run_tests.sh
 ```
## TODO
* cleanup dependency on elastic in tests