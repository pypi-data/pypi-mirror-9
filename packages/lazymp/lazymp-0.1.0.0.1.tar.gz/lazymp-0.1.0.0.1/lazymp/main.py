import re 

class SharedVariables:
    def __init__(self):
        self.shared = {}

    def register(self, variable):
        self.shared[variable] = variable

    def dump(self):
        return self.shared.keys()

    def clean(self):
        self.shared = {}

class Parser:
    space_prog = re.compile("^( *)[^ ]*")
    comment_prog = re.compile("(#.*)$")
    for_prog = re.compile("for ([^ ]+) in ([^:]+):")

    def __init__(self, inputfilename):
        self.f = open(inputfilename)
        self.last_line = None
        self.last_struct = None

    def parse_for(self, line):
        tmp = Parser.for_prog.search(line)

        if tmp is None:
            return None, None
        else:
            line, line_struct = self.parse_line(line)

            return line, {'indention' : line_struct['indention'], 
                            "variable": tmp.group(1), 
                            "iterate_list": tmp.group(2)}

    def parse_blcok(self):
        block_lines = []
        last_indention = None
        while True:
            line, struct = self.parse()
            if line is None:
                break

            if last_indention is None:
                last_indention = struct['indention']
                block_lines.append(line)
            else:
                if last_indention > struct['indention']: # next block
                    self.last_line, self.last_struct = line, struct
                    break
                else:
                    block_lines.append(line)

        return block_lines, {'indention': last_indention}

    def parse(self):
        if self.last_line is not None:
            tmp_line = self.last_line
            tmp_struct = self.last_struct
            self.last_line = None
            self.last_struct = None
            return tmp_line, tmp_struct

        self.line = self.f.readline()

        # last line
        if self.line == '':
            return None, None  

        self.line = self.line[:-1]

        return self.parse_line(self.line)

    def parse_line(self, line):
        # indention 
        space_match = Parser.space_prog.match(self.line)
        indention = 0 
        if space_match is not None:
            indention = len(space_match.group(1))

        # comment
        comment_match = Parser.comment_prog.match(self.line)
        comment = None
        if comment_match is not None:
            comment = comment_match.group(1)

        # tokens :
        tokens = []
        split_tmp = [t for t in self.line.split(" ") if len(t) > 0]
        pragma_tokens = None
        for i in xrange(len(split_tmp)):
            if len(split_tmp[i]) == 0:
                continue
            if split_tmp[i] == Annotation.PREFIX:
                pragma_tokens = split_tmp[i:]
                break
            if split_tmp[i] == "#":
                break
            tokens.append(split_tmp[i])

        return self.line, {
                            "indention": indention, 
                            "comment": comment, 
                            "tokens": tokens, 
                            "pragma_tokens": pragma_tokens
                            }
    def close(self):
        self.f.close()

class Writer:
    def __init__(self, outputfilename):
        self.f = open(outputfilename, "w")

    def write(self, line):
        print >> self.f, line

    def write_block(self, block):
        for line in block:
            self.write(line)

    def close(self):
        self.f.close()

class Template:
    @staticmethod
    def def_function(variable, function_name, indention=0):
        return "%sdef %s(%s):" %(" " * indention, function_name, variable)
    @staticmethod
    def define_variable(left, right, indention=0):
        return "%s%s = %s" %(" " * indention, left, right)
    @staticmethod
    def return_variable(variable, indention=0):
        return "%sreturn %s" % (" "*indention, variable)

    @staticmethod
    def import_moudle(module, package=None,abbr=None, indention=0):
        indention_str = " " * indention
        if package is None:
            if abbr is None:
                return "%simport %s" %(indention_str, module)
            else:
                return "%simport %s as %s" %(indention_str, module, abbr)            
        else:
            if abbr is None:
                return "%sfrom %s import %s" %(indention_str, package, module)
            else:
                return "%sfrom %s import %s as %s" %(indention_str, package, module, abbr) 

    @staticmethod
    def execute_function(function_name, variables, indention=0):
        if type(variables) is str:
            variables_str = variables
        elif type(variables) is list:
            variables_str = ", ".join(variables)
        return "%s%s(%s)" % (" "* indention, function_name, variables_str)

class Annotation:
    PREFIX = "#pragma"
    SHARED_VARIABLES = "#pragma shared"
    PARALLEL_FOR = "#pragma omp parallel for"

class STATE:
    NORMAL = 1
    PARALLEL_FOR = 2

class PragmaTranslator:
    parallel_prog = re.compile(Annotation.PARALLEL_FOR)
    shared_variables_prog = re.compile(Annotation.SHARED_VARIABLES)
    PARALLEL_FOR = 1 
    SHARED_VARIABLES = 2
    ELSE = 3

    @staticmethod
    def parse(pragma_tokens):
        command = " ".join(pragma_tokens)
        tmp = PragmaTranslator.parallel_prog.match(command)
        if tmp is not None:
            return PragmaTranslator.PARALLEL_FOR 
        
        tmp = PragmaTranslator.shared_variables_prog.match(command)
        if tmp is not None:
            return PragmaTranslator.SHARED_VARIABLES
        
        return PragmaTranslator.ELSE

class Translator:
    def __init__(self, inputfilename, outputfilename):
        self.parser = Parser(inputfilename)
        self.writer = Writer(outputfilename)
        self.state = STATE.NORMAL
        self.shared_variables = SharedVariables()
        self.threads = 4

    def process_parallel_for(self, line, struct):
        # parallel for 
        parallel_line, parallel_struct = self.parser.parse_for(line)
        if parallel_line is None:
            # cannot parse parallel for correctly
            self.writer.write(line)
        else:
            # parse block 
            block, block_struct = self.parser.parse_blcok()
            # rewrite code
            self.writer.write(
                Template.def_function(
                    variable=parallel_struct['variable'],
                    function_name="core",
                    indention=parallel_struct['indention']
                )
            )
            # insert registered code 
            self.writer.write(
                Template.define_variable(
                    left = "__shared__",
                    right= "{}",
                    indention=block_struct['indention']
                )
            )
            # import copy 
            self.writer.write(
                Template.import_moudle(
                    module="copy",
                    indention=block_struct['indention']
                )
            )

            for registered_variable in self.shared_variables.dump():
                self.writer.write(
                    Template.define_variable(
                        left = "__shared__['%s']" % registered_variable,
                        right = "copy.deepcopy(%s)" % registered_variable,
                        indention=block_struct['indention'] 
                    )
                )

            # insert block, replace register variable with __shared['%s'] 
            block_text = "\n".join(block)
            for registered_variable in self.shared_variables.dump():
                block_text = block_text.replace(registered_variable, "__shared__['%s']" % registered_variable) 
            self.writer.write(block_text)

            # insert footer 
            self.writer.write(
                Template.return_variable(
                    variable="__shared__",
                    indention=block_struct['indention']
                )
            )
            # insert import 
            self.writer.write(
                Template.import_moudle(
                    package="pathos.multiprocessing",
                    module="ProcessingPool",
                    indention=parallel_struct['indention']
                )
            )
            # insert __shared__ = ProcessingPool(4).map(core, range(size_x))
            self.writer.write(
                    Template.define_variable(
                        left = "__shared__",
                        right = "ProcessingPool(%d).map(core, %s)" %(
                            self.threads, 
                            parallel_struct['iterate_list']),
                        indention=parallel_struct['indention'] 
                    )
            )
            # insert Merge function 
            tmp_list =[ ]
            for registered_variable in self.shared_variables.dump():
                tmp_list.append("'%s': %s" % (registered_variable, registered_variable) )     
            registered_variable_dict_str = "{ %s }" %(", ".join(tmp_list))

            self.writer.write(
                Template.execute_function(
                    function_name="join_shared",
                    variables=["__shared__", registered_variable_dict_str],
                    indention=parallel_struct['indention']
                )
            )

    def process_shared_variables(self, line, struct):
        # need to check token struct first
        assert re.search("[^=]+=[^ ]+", line) ==None, "'%s' is not a delaration of variable."

        # parse variable name 
        variable = struct['tokens'][0]

        # register
        self.shared_variables.register(variable)

    def header(self):
        self.writer.write(
            Template.import_moudle(
                package="lazymp.helpers",
                module="join_dict"
            )
        )
        self.writer.write(
            Template.import_moudle(
                package="lazymp.helpers",
                module="join_shared"
            )
        )

    def run(self):
        self.header()

        while True:
            line, struct = self.parser.parse()
            if line == None:
                break

            if self.state == STATE.NORMAL:
                if struct.get('pragma_tokens') is not None:
                    pragma_type = PragmaTranslator.parse(struct.get('pragma_tokens'))
                    if pragma_type == PragmaTranslator.PARALLEL_FOR:
                        self.process_parallel_for(line, struct)
                    elif pragma_type == PragmaTranslator.SHARED_VARIABLES:
                        self.process_shared_variables(line, struct)
                        self.writer.write(line)
                    else:
                        self.writer.write(line)
                else:
                    self.writer.write(line)

    def close(self):
        self.parser.close()
        self.writer.close()

def translate(inputfilename, outputfilename):
    translator = Translator(inputfilename, outputfilename)
    translator.run()
    translator.close()

if __name__ == "__main__":
    import sys
    inputfilename = sys.argv[1]
    outputfilename = sys.argv[2]
    translate(inputfilename, outputfilename)
