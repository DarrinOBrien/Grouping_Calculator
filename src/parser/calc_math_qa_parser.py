import re
import copy
import sympy
import ast
from pathlib import Path
from datasets import load_dataset, load_from_disk
import random

class Calc_Math_QA_Processer():
    def __init__(self, special_func=set(), special_var=set()):
        self.special_func = special_func
        special_var.add("pi")
        self.special_var = special_var

        self.calc_start = '<gadget id="calculator">'
        self.calc_end = '</gadget>'
        self.out_start = '<output>'
        self.out_end = '</output>'
    
    def process_chain(self, ds):
        """
        Combines outputs of the following methods: [`extract_formatted`, `find_sub_expressions_simplified_expressions`, `find_operands_all_numbers`, `find_operators`, `update_special_func`]
        Returns: \n
        - `expressions`: The expressions in the calculation
        - `solutions`: The solutions to the expressions
        - `full_equations`: The formatted and compressed expressions and solutions put together
        - `has_sub_expressions`: Whether or not the expressions had any sub-expressions inside
        - `has_function_calls`: Whether or not the expression required the Sympy module for advanced calculations (e.g. lcm)
        - `has_special_variables`: Whether or not the expression required the math module for parsing mathematical symbols (e.g. pi)
        - `single_func`: Whether or not the expression primarily consists of a single func (e.g. log(3*2))
        - `sub_expressions`: The actual sub-expressions, if any, in a list format
        - `sub_expression_results`: The result of the actual sub-expressions, if any
        - `simplified_expressions`: The simplified expression consisting only of floats/integers with a single operator (e.g. (2*3)+5 -> 6+5)
        - `operands`: All numbers involved in the expression
        - `main_operands`: The primary 2 numbers involved in the expression
        - `all_numbers`: All numbers including the operands, sub expression results, and answers
        - `operators`: All symbols, [-+/*%**] and/or special functions, involved in the expression
        - `main_operators`: Single primary operator involved in the expression
        """
        sample = ds["chain"]

        extracted_formatted = self.extract_formatted(sample)
        expressions, solutions, full_equations = extracted_formatted["expressions"], extracted_formatted["solutions"], extracted_formatted["full_equations"]

        self.update_special_func(full_equations)
        
        find_sub_expressions_simplified_expressions = self.find_sub_expressions_simplified_expressions(expressions)
        has_sub_express, has_function_calls, has_special_vars, is_single_func, sub_express, sub_express_results, simplified_expressions = find_sub_expressions_simplified_expressions["has_sub_expressions"], find_sub_expressions_simplified_expressions["has_function_calls"], find_sub_expressions_simplified_expressions["has_special_variables"], find_sub_expressions_simplified_expressions["single_func"], find_sub_expressions_simplified_expressions["sub_expressions"], find_sub_expressions_simplified_expressions["sub_expression_results"], find_sub_expressions_simplified_expressions["simplified_expressions"]

        find_operands_simplified_expression_all_numbers = self.find_operands_all_numbers(expressions, simplified_expressions, solutions)
        operands, main_operands, all_numbers = find_operands_simplified_expression_all_numbers["operands"], find_operands_simplified_expression_all_numbers["main_operands"], find_operands_simplified_expression_all_numbers["all_numbers"]

        find_operators = self.find_operators(expressions, simplified_expressions, is_single_func)
        operators, main_operators = find_operators["operaters"], find_operators["main_operators"]

        return {
            "expressions": expressions,
            "solutions": solutions,
            "full_equations": full_equations,
            "has_sub_expressions": has_sub_express,
            "has_function_calls": has_function_calls,
            "has_special_variables": has_special_vars,
            "is_single_func": is_single_func,
            "sub_expressions": sub_express,
            "sub_expression_results": sub_express_results,
            "operands": operands,
            "main_operands": main_operands,
            "simplified_expressions": simplified_expressions,
            "all_numbers": all_numbers,
            "operators": operators,
            "main_operators": main_operators,
        }
    
    def extract_formatted(self, sample):
        '''
        Formats and compresses the equations while parsing the expressions and solutions.
        Returns the following: \n
        - `expressions`: The expressions in the calculation
        - `solutions`: The solutions to the expressions
        - `full_equations`: The formatted and compressed expressions and solutions put together
        '''
        expressions = [re.sub(rf'\s+|_', '', expression) for expression in re.findall(rf"\{self.calc_start}(.*?)\{self.calc_end}", sample)]
        solutions = [re.sub(r'_|around|^.*=\s*| ', "", solution) for solution in re.findall(rf"\{self.out_start}(.*?)\{self.out_end}", sample)]
        full_equations = [f"{expression}={solution}" for expression, solution in zip(expressions, solutions)]

        return {
            "expressions": expressions,
            "solutions": solutions,
            "full_equations": full_equations
        }
    
    def find_sub_expressions_simplified_expressions(self, expressions):
        """
        Finds sub-expressions, if any, within the general expression.\n
        Sub-expressions are defined as any calculation using an operator (+-*/%**) within a series of parantheses.\n
        Returns the following: \n
        - `has_sub_expressions`: Whether or not the expressions had any sub-expressions inside
        - `has_function_calls`: Whether or not the expression required the Sympy module for advanced calculations (e.g. lcm)
        - `has_special_variables`: Whether or not the expression required the math module for parsing mathematical symbols (e.g. pi)
        - `single_func`: Whether or not the expression primarily consists of a single func (e.g. log(3*2))
        - `sub_expressions`: The actual sub-expressions, if any, in a list format
        - `sub_expression_results`: The result of the actual sub-expressions, if any
        - `simplified_expressions`: The simplified expression consisting only of floats/integers with a single operator (e.g. (2*3)+5 -> 6+5)
        """

        has_function_calls = [False for _ in range(len(expressions))]
        has_special_vars = [False for _ in range(len(expressions))]
        is_single_func = [None for _ in range(len(expressions))]
        simplified_expressions = copy.deepcopy(expressions)

        sub_express = [[] for _ in range(len(expressions))]
        has_sub_express = [False for _ in sub_express]
        sub_express_results = [[] for _ in sub_express]
        for i in range(len(expressions)):
            temp_express = expressions[i]

            def is_single_function(expr, allowed_funcs=list(self.special_func)):
                try:
                    tree = ast.parse(expr, mode='eval')
                    node = tree.body

                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name) and node.func.id in allowed_funcs:
                            return node.func.id
                    return None
                except Exception:
                    return None
            
            result = is_single_function(temp_express)
            if result:
                is_single_func[i] = result
                has_function_calls[i] = True
                single_func = result
                temp_express = temp_express[len(single_func)+1:-1]
            
            for func in self.special_func:
                if func in temp_express:
                    has_function_calls[i] = True
            for var in self.special_var:
                if var in temp_express:
                    has_special_vars[i] = True

            def get_primary_subexpressions(expr):
                root = ast.parse(expr, mode="eval").body
                subs = []

                if isinstance(root, ast.BinOp):
                    for side in (root.left, root.right):
                        subs.extend(extract_operand(side))

                elif isinstance(root, ast.Call):
                    subs.extend(root.args)

                return [ast.unparse(s) for s in subs]

            def extract_operand(node):
                if isinstance(node, ast.Call):
                    return node.args

                if isinstance(node, (ast.BinOp, ast.UnaryOp)):
                    return [node]

                return []

            found_sub_expressions = get_primary_subexpressions(temp_express)
            sub_express[i] = [re.sub(r"\s+", "", sub_e) for sub_e in found_sub_expressions]
            if sub_express[i]:
                has_sub_express[i] = True
                for j in range(len(sub_express[i])):
                    sub_express_part_result = str(sympy.sympify(sub_express[i][j]).evalf())
                    sub_express_results[i].append(sub_express_part_result)
                    try:
                        if float(sub_express[i][j]) == float(sub_express_part_result):
                            continue
                    except:
                        temp_express = re.sub(re.escape(sub_express[i][j]), sub_express_part_result, temp_express)

            if is_single_func[i]:
                simplified_expressions[i] = f"{single_func}({temp_express})"
            else:
                def correct_paren(expr):
                    open_paren = expr.count("(")
                    close_paren = expr.count(")")
                    if open_paren > close_paren:
                        expr += ")" * (open_paren-close_paren)
                    elif open_paren < close_paren:
                        expr = "(" * (close_paren-open_paren) + temp_express
                    return expr
                
                for func in self.special_func:
                    if func in temp_express:
                        def replace_func(match):
                            inner = match.group(1)
                            res_express = correct_paren(f"{func}({inner})")
                            return str(sympy.sympify(res_express).evalf())
                        temp_express = re.sub(rf"{func}\((.*?)\)", replace_func, temp_express)
                for var in self.special_var:
                    if var in temp_express:
                        def replace_var(match):
                            return str(sympy.sympify(f"{var}").evalf())
                        temp_express = re.sub(rf"{var}", replace_var, temp_express)
                simplified_expressions[i] = temp_express
            
        return {
            "has_sub_expressions": has_sub_express,
            "has_function_calls": has_function_calls,
            "has_special_variables": has_special_vars,
            "single_func": is_single_func,
            "sub_expressions": sub_express,
            "sub_expression_results": sub_express_results,
            "simplified_expressions": simplified_expressions,
        }

    def find_operands_all_numbers(self, expressions, simplified_expressions, solutions):
        """
        Finds operands within the general expression, formats the primary operands, and crafts together all numbers.
        Returns the following: \n
        - `operands`: All numbers involved in the expression
        - `main_operands`: The primary 2 numbers involved in the expression
        - `all_numbers`: All numbers including the operands, sub expression results, and answers
        """
        operand_pattern = r"-?\d*\.?\d+"
        for var in self.special_var:
            operand_pattern = operand_pattern + f"|{var}"

        operands = [re.findall(operand_pattern, expression) for expression in expressions]
        main_operands = [re.findall(operand_pattern, simplified_expression) for simplified_expression in simplified_expressions]

        all_numbers = copy.deepcopy(operands)
        for i in range(len(all_numbers)):
            if all_numbers[i] != main_operands[i]:
                for j in range(len(all_numbers[i])):
                    if j < len(main_operands[i]) and all_numbers[i][j] != main_operands[i][j]:
                        all_numbers[i].append(main_operands[i][j])
            all_numbers[i].append(solutions[i])
        
        return {
            "operands": operands,
            "main_operands": main_operands,
            "all_numbers": all_numbers
        }
    
    def find_operators(self, expressions, simplified_expressions, is_single_func): 
        """
        Finds operators (1+) and main operaters (1) in the expression. 
        Returns: \n
        - `operators`: All symbols, [-+/*%**] and/or special functions, involved in the expression
        - `main_operators`: Single primary operator involved in the expression
        """
        operator_pattern = r"\*\*|[-+/*%]"

        for func in self.special_func:
            operator_pattern = rf"{func}|" + operator_pattern

        operators = [re.findall(operator_pattern, expression) for expression in expressions]
        main_operators = []
        for i in range(len(simplified_expressions)):
            if is_single_func[i]:
                main_operators.append(is_single_func[i])
            else:
                main_operators.append(re.findall(operator_pattern, simplified_expressions[i])[0])

        return {
            "operaters": operators,
            "main_operators": main_operators,
        }
    
    def update_special_func(self, full_equations):
        """
        Adds new, unseen Sympy functions to `self.special_func` for dynamic calculations.
        """
        arr = set()
        for equation in full_equations:
            founds = re.findall(r'[a-zA-Z]+', equation)
            for found in founds:
                if found and found not in self.special_var:
                    arr.add(found)
        self.special_func = self.special_func.union(arr)

'''
print(f"Expressions: {results["expressions"]}")
print(f"Solutions: {results["solutions"]}")
print(f"Full Equations: {results["full_equations"]}")
print(f"Has Sub-Expressions: {results["has_sub_expressions"]}")
print(f"Has Function-Calls: {results["has_function_calls"]}")
print(f"Has Special Variables: {results["has_special_variables"]}")
print(f"Sub-Expressions: {results["sub_expressions"]}")
print(f"Sub-Expression Results: {results["sub_expression_results"]}")
print(f"Operands: {results["operands"]}")
print(f"Main Operands: {results["main_operands"]}")
print(f"Simplified Expressions: {results["simplified_expressions"]}")
print(f"All Numbers: {results["all_numbers"]}")
print(f"Operators: {results["operators"]}")
print(f"Main Operators: {results["main_operators"]}")
'''

def process_dataset(ds_path):
    """
    Loads the Calc Math QA dataset. This function will process the dataset if not already and save it to the specified path. Returns train and val processed dataset dictionaries.
    
    :param ds_path: Path to the intended or residing dataset shards
    """
    if Path(ds_path).is_dir():
        train = load_from_disk(f"{ds_path}/train")
        val = load_from_disk(f"{ds_path}/val")

        return train, val
    else:
        ds = load_dataset("MU-NLPC/Calc-math_qa", "original-splits") # https://huggingface.co/datasets/MU-NLPC/Calc-math_qa
        processor = Calc_Math_QA_Processer()

        unused_columns = ["question", "result", "result_float", "question_without_options", "options", "linear_formula", "rationale", "category"]

        train = ds["train"].remove_columns(unused_columns)
        val = ds["validation"].remove_columns(unused_columns)

        train = train.map(processor.process_chain)
        val = val.map(processor.process_chain)

        unused_columns = ["chain", "annotated_formula"]
        train = train.remove_columns(unused_columns)
        val = val.remove_columns(unused_columns)

        train.save_to_disk(f"{ds_path}/train")
        val.save_to_disk(f"{ds_path}/val")

        return train, val
    
def combine_dicts(samples):
    """
    Combines the dictionaries of selected samples and randomizes the order. Intended for randomizing data when training the GNN. Returns a single dictionary of the combined samples. 
    
    :param samples: List of samples to combine
    """
    combined_dict = {"expressions": [],
            "solutions": [],
            "full_equations": [],
            "has_sub_expressions": [],
            "has_function_calls": [],
            "has_special_variables": [],
            "is_single_func": [],
            "sub_expressions": [],
            "sub_expression_results": [],
            "operands": [],
            "main_operands": [],
            "simplified_expressions": [],
            "all_numbers": [],
            "operators": [],
            "main_operators": [],}
    for sample in samples:
        for key in sample.keys():
            if key == "id":
                continue
            combined_dict[key].extend(sample[key])

    indices = list(range(len(combined_dict["expressions"])))
    random.shuffle(indices)
    for key in combined_dict.keys():
        combined_dict[key] = [combined_dict[key][i] for i in indices]
    
    return combined_dict