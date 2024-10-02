### Purpose

This set of tools (RanRead, RanWrite, and the combined RanIO) is used to generate random read and write events within a database (or pair of databases) to test the IO speed of IRIS running on a specified hardware setup. While Read operations can be measured in the usual Input/Output operations per second (IOPS) since they're direct disk reads, write events are sent to the database and thus their physical writes are managed by IRIS's write daemon.  

Results gathered from the IO tests will vary from configuration to configuration based on the IO sub-system. Before running these tests, ensure corresponding operating system and storage level monitoring are configured to capture IO performance metrics for later analysis. The suggested method is by running the System Performance tool that comes bundled within IRIS. Please note that this is an update to a previous release, which can be found [here](https://community.intersystems.com/post/random-read-io-storage-performance-tool).

<!--break-->

### Setup

Create an empty (pre-expanded) database called RAN at least twice the size of the memory of the physical host to be tested. Ensure empty database is at least four times the storage controller cache size. The database needs to be larger than memory to ensure reads are not cached in file system cache. You can create manually or use the following methods to automatically create a namespace and database.

<pre style="border: 1px solid rgb(204, 204, 204); padding: 5px 10px; background: rgb(238, 238, 238);">USER> do ##class(PerfTools.RanRead).Setup("/ISC/tests/TMP","RAN",200,1)</pre>

OR

<pre style="border: 1px solid rgb(204, 204, 204); padding: 5px 10px; background: rgb(238, 238, 238);">USER> do ##class(PerfTools.RanIO).Setup("/ISC/tests/TMP","RAN",200,1)</pre>

### Methodology

Start with a small number of RanRead processes and 30-60 second run times. Then increase the number of processes, e.g. start at 10 jobs and increase by 10, 20, 40 etc. Continue running the individual tests until response time is consistently over 10ms or calculated IOPS is no longer increasing in a linear way. 

As a guide, the following response times for 8KB and 64KB Database Random Reads (non-cached) are usually acceptable for all-flash arrays:

  * Average &lt;= 2ms
  * Not to exceed &lt;= 5ms

### Run


### Results


### Analysis


### Clean Up

