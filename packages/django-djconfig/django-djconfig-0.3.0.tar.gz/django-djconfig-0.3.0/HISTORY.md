0.3.0
==================

* Drops support for django 1.5 and 1.6 (for no special reason)
* Support for django 1.8
* Adds migrations
* Raise AttributeError if the config key/attr is not found
* Fix race condition that caused returning non existent values (None) if the config was not fully loaded
* Huge code refactor

0.2.0
==================

* Configuration is lazy loaded, now. This means the database will get queried the first time an option is accessed *(ie: `confi.my_first_key`)*
* Only `config` and `register` are available for importing from the root module *djconfig*.