# Testing

KotorBlender code is tightly coupled to Blender Python API, making it impractical to test KotorBlender outside of Blender. At the same time, Blender is a moving target, where new versions of Blender often introduce breaking changes. Therefore, in addition to manual testing, it is a good idea to have an automated test suite, that we are able to run quickly and often, and that is able to verify that addon functionality works as expected across multiple versions of Blender.

We can achieve the above by executing test scripts in Blender in background mode. These scripts should invoke KotorBlender functionality and verify results, for example, import and export varying KotOR and TSL models and verify that exported models are equivalent to originals.

In order to run the test suite, execute the following from a terminal on Linux or use MSYS on Windows:

1. `DATA_DIR=? [TSL=?] [OFFSET=?] [LIMIT=?] make test`

where:

- `DATA_DIR` is path to a directory containing assets extracted from BIF archives
- `TSL` is a flag indicating use of TSL model format (0 or 1, defaults to 0)
- `OFFSET` is an offset into the list of models in the data directory (defaults to 0)
- `LIMIT` is the maximum number of models to process (defaults to 50)
