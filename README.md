# DTCC Modules

DTCC Modules is a collection of modules for DTCC Platform.

Each module provides the platform with a specific capability for data
generation, data analysis, or simulation by wrapping a specific tool.

Each module is designed as a Docker container that provides a common
interface to the tool being wrapped and listens to requests (Pub/Sub).

This project is part the
[Digital Twin Platform (DTCC Platform)](https://gitlab.com/dtcc-platform)
developed at the
[Digital Twin Cities Centre](https://dtcc.chalmers.se/)
supported by Sweden’s Innovation Agency Vinnova under Grant No. 2019-421 00041.

## Documentation

* [Introduction](./doc/introduction.md)
* [Installation](./doc/installation.md)
* [Usage](./doc/usage.md)
* [Development](./doc/development.md)

## Authors (in order of appearance)

* [Anders Logg](http://anders.logg.org)
* [Dag Wästerberg](https://chalmersindustriteknik.se/sv/medarbetare/dag-wastberg/)

## License

DTCC Modules is licensed under the
[MIT license](https://opensource.org/licenses/MIT).

Copyright is held by the individual authors as listed at the top of
each source file.



{
  "task_id": "55d83bc3",
  "module_name": "dtcc-module-examples",
  "tool": "upload-download-minio"
  "parameters": "{\"bucket_name\":\"dtcc\", \"prefix\":\"/HelsingborgHarbour2022\"}"
}