# BenchExec: benchexec
## Benchmarking a Collection of Runs

The program `benchexec` provides the possibility to easily benchmark
multiple executions of a tool in one go.

### Input for benchexec
`benchexec` uses as input an XML file that defines the command(s) to execute,
the resource limits, and the tasks for which the command should be run.
A complete definition of the input format can be found in the file
[doc/benchmark.xml](benchmark.xml),
and examples in [doc/benchmark-example-rand.xml](benchmark-example-rand.xml)
and [doc/benchmark-example-cbmc.xml](benchmark-example-cbmc.xml).
A document-type definition with a formal specification of such files can be found in
[doc/benchmark.dtd](benchmark.dtd).
Such benchmark-definition files consist of a root tag `<benchmark>`
that has attributes for the tool to use and the resource limits.
Nested `<rundefinition>` tags allow to specify multiple different configurations of the tool,
each of which is executed with the tasks.
The tasks are defined in nested `<tasks>` tags,
either with `<include>` tags (which directly specify patterns of input files)
or with `<includesfile>` tags (which specify text files with file-name patterns on each line).
Relative file names in these tags are interpreted as relative to the directory of the XML file. 
A task that does not directly correspond to an input file can be defined
with a `<withoutfiles>` tag within a `<tasks>` tag,
giving the identifier of the task as tag content.
This can be used for example to declare multiple tasks for the same input file
but with different entry points.
Command-line arguments for the tool are given with `<option>` tags,
which can appear directly inside the root tag (always effective),
inside a `<rundefinition>` tag (affective for this configuration),
or inside a `<tasks>` tag (affective only for this subset of tasks for all configurations).
Note that you need to use a separate `<option>` tag for each argument,
putting multiple arguments separated by spaces into a single tag will not have the desired effect.

BenchExec allows to check whether the output of the tool matches the expected result
for a given task, and to categorize the results accordingly.
This is currently only available for the domain of software verification,
where `benchexec` uses a
[property file as defined by the International Competition on Software Verification](http://sv-comp.sosy-lab.org/2015/rules.php).
Such files can be specified with the tag `<propertyfile>`.

Inside the `<option>` tag and other tags some variables can be used
that will be expanded by BenchExec. The following variables are supported:

    ${benchmark_name}       Name of benchmark execution
    ${benchmark_date}       Timestamp of benchmark execution
    ${benchmark_path}       Directory of benchmark XML file
    ${benchmark_path_abs}   Directory of benchmark XML file (absolute path)
    ${benchmark_file}       Name of benchmark XML file (without path)
    ${logfile_path}         Directory where tool-output files will be stored
    ${logfile_path_abs}     Directory where tool-output files will be stored (absolute path)
    ${rundefinition_name}   Name of current run definition
    ${inputfile_name}       Name of current input file (without path)
    ${inputfile_path}       Directory of current input file
    ${inputfile_path_abs}   Directory of current input file (absolute path)

For example, to pass as additional tool parameter the name of a file
that is in the same directory as each input file, use

    <option name="-f">${inputfile_path}/additional-file.txt</option>

### Adopting benchexec for a specific tool
In order to know how to execute a tool and how to interpret its output,
`benchexec` needs a tool-specific Python module
with functions for creating the appropriate command-line arguments for a run etc.
Such modules need to define a class `Tool` that inherits from `benchexec.tools.template.BaseTool`.
This class also contains the [documentation](../benchexec/tools/template.py)
on how to write such a module.

BenchExec already provides such [ready-to-use modules for some common tools](../benchexec/tools/).
These are written such that they try to find the executable of the tool
either in a directory of the PATH environment variable or in the current directory.
To point BenchExec to a location of the executable, the easiest way is to adjust PATH accordingly:

    PATH=/path/to/tool/directory:$PATH benchexec ...


### Starting benchexec
To use `benchexec`, simply call it with an XML file with a benchmark definition:

    benchexec doc/benchmark-example-rand.xml

Command-line arguments to `benchexec` allow to override the defined resource limits.
If one wants to execute only a subset of the defined benchmark runs,
the name of the `<rundefinition>` and/or `<tasks>` tags
that should be executed can also be given on the command line.
To start multiple executions of the benchmarked tool in parallel
(if the local machine has enough resources),
use the parameter `--numOfThreads`.
Example:

    benchexec doc/benchmark-example-rand.xml --tasks "XML files" --limitCores 1 --timelimit 10 --numOfThreads 4

The full set of available parameters can be seen with `benchexec -h`.

`benchexec` produces as output the results and resource measurements
of all the individual tool executions in XML files
from which tables can be created using `table-generator`.
There is one file per run definition/tool configuration,
and additional files for each subset of tasks
(all by default in directory `./result/`).
A document-type definition with a formal specification of such result files can be found in
[doc/benchmark-result.dtd](benchmark-result.dtd).
The output of the tool executions is stored in additional files in a sub-directory.
If the target directory for the output files (specified with `--outputpath`)
is a git repository without uncommitted changes and the option `--commit`
is specified, `benchexec` will add and commit all created files to the git repository.
One can use this to create a reliable archive of experimental results.


### Extending BenchExec
BenchExec executes all runs on the local machine.
In some cases, it might be desired to use for example some cloud service
to execute the commands, and BenchExec should only handle the benchmark definition
and aggregate the results.
This can be done by replacing the module `benchexec.localexecution`,
which is responsible for executing a collection of runs, by something else.
To do so, inherit from the BenchExec main class `benchexec.BenchExec`
and override the necessary methods such as `load_executor`
(which by default returns the `benchexec.localexecution` module),
`create_argument_parser` (to add your own command-line arguments) etc.
