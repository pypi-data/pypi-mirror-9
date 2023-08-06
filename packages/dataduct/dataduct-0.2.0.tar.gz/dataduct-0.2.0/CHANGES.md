# Changes in dataduct

### 0.2.0
- Travis integration for continous builds
- QA steps and logging to S3
- Visualizing pipeline
- Dataduct CLI updated as a single entry point
- RDS connections for scripts
- Bootstrap step for pipelines
- Backfill or delay activation
- Output path and input path options
- Script directory for transform step
- SQL sanatization for DBA actions
- SQL parser for select and create table statements
- Logging across the library
- Support for custom steps
- Pipeline dependency step
- Reduce verbosity of imports
- Step parsing is isolated in steps
- More examples for steps
- Sync config with S3
- Config overides with modes
- Rename keywords and safe config failure handling
- EMR Streaming support with hadoop 2
- Exceptions cleanup
- Read the docs support
- Creating tables automatically for various steps
- History table support
- EC2 and EMR config control from YAML
- Slack integration
- Support for Regions in DP

### 0.1.0
- Initial version of the dataduct library released
- Support for the following steps:
    - emr_streaming
    - extract-local
    - extract-s3
    - extract-rds
    - extract-redshift
    - load-redshift
    - sql-command
    - transform
- Examples and documentation added for all the steps
