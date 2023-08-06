# txBalanced

Online Marketplace Payments

*Note:* this library works with Balanced API version 1.1

This is the [Twisted](https://twistedmatrix.com/trac/) fork of the official Balanced Payments Python [library](https://github.com/balanced/balanced-python/). While this library is directly derived from the official python library, there are some areas where it is not completely compatible. For example:

* It is not possible to lazily iterate through paginated lists. You must instead load each page and iterate through the items in the page. (.all() will load everything, however, but be aware that it will load all results into memory)
* Any lookup that goes over the wire will return a deferred

## Installation

    pip install txbalanced

## Usage

View Balanced's online tutorial and documentation at https://www.balancedpayments.com/docs/overview?language=python (while noting the caveats above)
