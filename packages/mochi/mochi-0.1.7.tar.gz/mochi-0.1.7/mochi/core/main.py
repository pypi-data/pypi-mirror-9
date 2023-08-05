import argparse
import traceback
from pathlib import Path
import sys

from mochi import __version__, IS_PYPY
from .builtins import current_error_port, eval_sexp_str, eval_tokens
from mochi.parser.parser import lex, REPL_CONTINUE
from .global_env import global_env
from .translation import syntax_table, global_scope, translator


def output_code(code):
    import marshal

    marshal.dump(code, sys.stdout.buffer)


def compile_file(src_path, optimize=-1):
    # binding_name_set_stack[0].update(global_env.keys())
    py_ast = translator.translate_file(src_path)
    return compile(py_ast, src_path, 'exec', optimize=optimize)


def load_file(path, env):
    return exec(compile_file(path), env)


def execute_compiled_file(path):
    import marshal

    with open(path, 'rb') as compiled_file:
        return exec(marshal.load(compiled_file), global_env)


def interact():
    try:
        import readline
    except ImportError:
        pass

    while True:
        buffer = ''
        continuation_flag = False
        tokens = []
        while True:
            try:
                if continuation_flag:
                    s = input('... ')
                    if s == '\n':
                        continue
                    buffer = buffer + '\n' + s
                else:
                    s = input('>>> ')
                    if s == '\n':
                        continue
                    buffer = s
            except EOFError:
                print()
                sys.exit()

            try:
                lexer = lex(buffer, repl_mode=True)

                for last in lexer:
                    tokens.append(last)

                if len(tokens) == 0:
                    buffer = ''
                    continue

                if last is REPL_CONTINUE or last.name == 'COLON' or last.name == 'THINARROW':
                    continuation_flag = True
                    tokens = []
                    continue
                else:
                    break
            except Exception:
                traceback.print_exc(file=current_error_port)
                continuation_flag = False
                buffer = ''
                continue
        eval_tokens(tokens)


def init():
    import eventlet

    def eval_from_file(path_obj):
        """Evaluate sexpression in given file.
        """
        with path_obj.open() as fobj:
            expr = fobj.read()
        eval_sexp_str(expr)

    eventlet.monkey_patch(#os=True, # if 'os' is true, rply don't work.
                          socket=True,
                          select=True,
                          thread=True,
                          time=True)
    expr_path = Path(__file__).absolute().parents[1] / 'sexpressions'
    eval_from_file(expr_path / 'main.expr')
    if not IS_PYPY:
        eval_from_file(expr_path / 'cpython.expr')
    else:
        eval_from_file(expr_path / 'pypy.expr')

    eval_from_file(expr_path / 'del_hidden.expr')

    for syntax in {'for', 'each', 'while', 'break', 'continue'}:
        del syntax_table[syntax]
        del global_env[syntax]
        del global_scope[syntax]


def main():
    init()

    if len(sys.argv) > 1:
        arg_parser = argparse.ArgumentParser(
            description='Mochi is a programming language.')
        arg_parser.add_argument('-v', '--version', action='version', version=__version__)
        arg_parser.add_argument('-c', '--compile', action='store_true')
        arg_parser.add_argument('-e', '--execute-compiled-file', action='store_true')
        arg_parser.add_argument('file', nargs='?', type=str)
        args = arg_parser.parse_args()

        if args.file:
            if args.compile:
                output_code(compile_file(args.file, optimize=2))
            elif args.execute_compiled_file:
                execute_compiled_file(args.file)
            else:
                load_file(args.file, global_env)
            sys.exit(0)
    else:
        interact()


if __name__ == '__main__':
    main()
