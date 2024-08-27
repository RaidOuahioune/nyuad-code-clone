import ast
import astor
import argparse
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import local
import random
from tqdm import tqdm
from transformations.transformer import CodeTransformer, transformation_names,non_clone_transformation_names

# Create thread-local storage
thread_local = local()
csv_path = "meta_clone.csv"
csv_non_clone_path="meta_non_clones.csv"
clone_count_dict={'clone':0,'not_clone':0}

def get_transformer():
    if not hasattr(thread_local, 'transformer'):
        thread_local.transformer = CodeTransformer()
    return thread_local.transformer

def use_main_transformer(code_snippet):
    transformer = get_transformer()
    # Parse code snippet into AST
    tree = ast.parse(code_snippet)
    
    # Transform the AST
    transformed_tree = transformer.visit(tree)
    
    # Convert AST back to source code
    new_code_snippet = astor.to_source(transformed_tree).strip()
    
    return new_code_snippet

def process_single_snippet(snippet, is_clone):
    transformer = get_transformer()
    # Apply transformations
    snippet_2 = use_main_transformer(snippet)
    
    # Choose the correct CSV path based on whether it's a clone or not
    path = csv_path if is_clone else csv_non_clone_path
    snippet_2,clone_status = transformer.apply_transformations(snippet_2, csv_file_path=path, is_clone=is_clone)
    
    return snippet, snippet_2, clone_status

def process_code_files(input_file, output_file):
    with open(input_file, 'r') as infile:
        snippets = infile.read().strip().split('\n\n')

    with open(output_file, 'w+') as outfile:
        # Initialize tqdm for progress tracking
        progress_bar = tqdm(total=len(snippets), desc="Processing Snippets")
        
        # Use ThreadPoolExecutor to parallelize the processing
        with ThreadPoolExecutor() as executor:
            future_to_snippet = {executor.submit(process_single_snippet, snippet,random.choice([True,False])): snippet for snippet in snippets}
            
            for future in as_completed(future_to_snippet):
                snippet_1 = future_to_snippet[future]
                try:
                    snippet_1, snippet_2,is_clone = future.result()
                    # Write the results to the output file
                    outfile.write(f"# snippet 1\n{snippet_1}\n")
                    outfile.write(f"# snippet 2\n{snippet_2}\n")
                    
                    outfile.write(f"# clone\n{int(is_clone)}\n\n\n\n")  # Assuming snippet 2 is a clone of snippet 1
                    if is_clone:
                        clone_count_dict['clone']+=1
                    else:
                        clone_count_dict['not_clone']+=1
                except Exception as e:
                    print(f"Exception occurred while processing snippet: {e}")
                finally:
                    progress_bar.update(1)  # Update progress bar for each completed future

        progress_bar.close()  # Close progress bar when done

def main():
    parser = argparse.ArgumentParser(description="Process and transform Python code snippets.")
    
    parser.add_argument("--input", default="level1.1.txt", type=str, help='Path to the input file containing code snippets.')
    
    args = parser.parse_args()
    with open(csv_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(transformation_names)
        
    with open(csv_non_clone_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(non_clone_transformation_names)

    process_code_files(args.input, f"clones_{args.input}")
    
    with open("clone_count.txt",'w') as f:
        f.write(str(clone_count_dict))
        print(f"Total Clones: {clone_count_dict['clone']}")
    

if __name__ == "__main__":
    main()
