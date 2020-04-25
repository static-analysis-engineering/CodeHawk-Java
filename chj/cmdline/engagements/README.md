### Scripts to invoke the CodeHawk Java Analyzer

### Overview

- [chj_analyze](#chj_analyze)
- [chj_analyze_cost](#chj_analyze_cost)
- [chj_analyze_taint](#chj_analyze_taint)
- [chj_add_callee_restriction](#chj_add_callee_restriction)
- [chj_add_loopbound](#chj_add_loopbound)
- [chj_report_costmodel](#chj_report_costmodel)
- [chj_report_taint_origins](#chj_report_taint_origins)
- [chj_report_taint_trail](#chj_report_taint_trail)

### Scripts

#### chj_analyze
Performs numerical analysis of the application and saves the
results in xml format. This script must be run before cost analysis
and taint analysis, and before any reports can be generated.
- positional arguments:
  - *appname*: name of engagement application (e.g., blogger)

#### chj_analyze_cost
Creates a cost model for the application for cpu time usage. Requires
that numerical analysis has already been performed (chj_analyze).
- positional arguments:
  - *appname*: name of engagement application (e.g., blogger)

#### chj_analyze_taint
Identifies all taint sources and constructs taint propagation
graphs for all methods. Requires that numerical analysis has
already been performed (chj_analyze).
- positional arguments:
  - *appname*: name of engagement application  (e.g., blogger)

#### chj_add_callee_restriction
Resolves virtual call to a concrete class by setting the target
class for one or more virtual call instructions in a method.
- positional arguments:
  - *appname*: name of engagement application (e.g., blogger)
  - *cmsix*: index of the method for which the call target class is to be added
  - *targetclass*: fully qualified name of the target class of the call instruction(s)

- keyword arguments:
  - *pcs* list of byte-code offsets: byte-code offsets of call instruction(s)

#### chj_add_loopbound
Adds a constant or symbolic loopbound to the userdata file of an
application method. If no userdata file exists yet for the class
of the method a new file is created.
- positional arguments:
  - *appname*: name of engagement application (e.g., blogger)
  - *cmsix*: index of the method to which the bound is to be added
    (can be obtained from reports, like the loop reports)
  - *pc*: program counter of the head of the loop

- keyword arguments:
  - *--constant* n: number of iterations
  - *--symbolic* name: name of symbolic constant for number of iterations

#### chj_report_costmodel
Reports the cpu time costs (in nanoseconds) for all application methods.
The report is divided in three sections. The first section lists all methods
that have a constant cost. Methods without any calls are marked with an
asterisk, methods with calls exclusively to methods without calls (that is,
the descendant callgraph has depth 1) are marked with two asterisks. The
second section lists all methods whose cost have distinct constant lower
and upper bound, sorted by increasing ratio between lower and upper bound
(the ratio is given as the first number). The last section lists the cost
for all other methods, that is, methods whose lower and/or upper bound include
symbolic method costs for callees or symbolic loop counters.
- positional arguments:
  - *appname*: name of engagement application (e.g., blogger)

- keyword arguments:
  - *--verbose*: show costs per basic block for methods with symbolic cost expressions
  - *--loops*: show costs for basic blocks that are part of loops
  - *--namerestriction* names: only report cost for functions that include one of the
    names as a substring

#### chj_report_taint_origins
Lists all or some of the taint sources present in the application as
identified by the analyzer.
- positional arguments:
  - *appname*: name of engagement application (e.g., blogger)

- keyword arguments:
  - *--source* name: only include sources that contain name as a substring

#### chj_report_taint_trail
Creates a graphical representation (using graphviz dot) of a taint
transmission graph. Requires prior generation of the graph data
using the script chj_analyze_taint_propagation for the given source id.
- positional arguments:
  - *appname*: name of engagagement application (e.g., blogger)
  - *taintsourceid*: identification number of the taint source (as obtained
    from the chj_report_taint_origins report)

- keyword arguments:
  - *--sink* name: (partial) name of a node to restrict the graph to paths
     to destinations that include the name
  - *--loops*: restrict the graph to paths to destinations that represent
	loop counters
