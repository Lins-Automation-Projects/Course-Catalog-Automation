import pandas as pd
from pathlib import Path
import time
from typing import Tuple, List
import sys
import argparse
import os

class CourseComparator:
    def __init__(self, active_path: str, corrected_path: str):
        self.active_path = Path(active_path)
        self.corrected_path = Path(corrected_path)
        self.active_courses: pd.DataFrame = None
        self.corrected_courses: pd.DataFrame = None

    def load_and_preprocess_data(self, file_path: Path, course_id_column: str = 'course_id') -> pd.DataFrame:
        """Load and preprocess course data with memory optimization."""
        print(f"\nLoading {file_path.name}...")
        
        # Only read the necessary column
        usecols = [course_id_column] if course_id_column != 'course_id' else ['course_id']
        
        if file_path.suffix.lower() == '.xlsx':
            df = pd.read_excel(file_path, usecols=usecols)
        else:
            df = pd.read_csv(file_path, usecols=usecols)
        
        # Rename column if needed
        if course_id_column != 'course_id':
            df.rename(columns={course_id_column: 'course_id'}, inplace=True)
        
        # Normalize course IDs and remove duplicates
        df['course_id'] = df['course_id'].astype(str).str.replace(r'\s+', '', regex=True).str.upper()
        initial_count = len(df)
        df.drop_duplicates(subset=['course_id'], inplace=True)
        final_count = len(df)
        
        if initial_count != final_count:
            print(f"Removed {initial_count - final_count} duplicate course IDs")
        
        print(f"Loaded {final_count} unique courses from {file_path.name}")
        return df

    def find_discrepancies(self) -> Tuple[List[str], List[str], dict]:
        """Find and analyze differences between datasets."""
        set1 = set(self.active_courses['course_id'])
        set2 = set(self.corrected_courses['course_id'])
        
        in_active_not_corrected = sorted(set1 - set2)
        in_corrected_not_active = sorted(set2 - set1)
        
        stats = {
            'total_active': len(set1),
            'total_corrected': len(set2),
            'missing_from_corrected': len(in_active_not_corrected),
            'missing_from_active': len(in_corrected_not_active),
            'matching_courses': len(set1.intersection(set2))
        }
        
        return in_active_not_corrected, in_corrected_not_active, stats

    def save_discrepancies(self, discrepancies: list, output_file: str):
        """Save discrepancies with additional context."""
        df = pd.DataFrame(discrepancies, columns=['course_id'])
        output_path = Path(output_file)
        df.to_csv(output_path, index=False)
        print(f"Saved {len(discrepancies)} discrepancies to {output_file}")

    def run_analysis(self):
        """Run the complete analysis with performance monitoring."""
        start_time = time.time()
        
        try:
            # Load datasets
            self.active_courses = self.load_and_preprocess_data(self.active_path, 'subj_cou_nbr')
            self.corrected_courses = self.load_and_preprocess_data(self.corrected_path)
            
            # Find discrepancies
            print("\nAnalyzing discrepancies...")
            active_not_corrected, corrected_not_active, stats = self.find_discrepancies()
            
            # Save results
            print("\nSaving results...")
            self.save_discrepancies(active_not_corrected, 'discrepancies_in_active_not_corrected.csv')
            self.save_discrepancies(corrected_not_active, 'discrepancies_in_corrected_not_active.csv')
            
            # Print analysis summary
            print("\n=== Analysis Summary ===")
            print(f"Total active courses: {stats['total_active']}")
            print(f"Total corrected courses: {stats['total_corrected']}")
            print(f"Matching courses: {stats['matching_courses']}")
            print(f"Missing from corrected dataset: {stats['missing_from_corrected']}")
            print(f"Missing from active dataset: {stats['missing_from_active']}")
            print(f"\nTotal processing time: {time.time() - start_time:.2f} seconds")
            
        except Exception as e:
            print(f"\nError: {str(e)}", file=sys.stderr)
            raise

def parse_arguments():
    parser = argparse.ArgumentParser(description='Compare two course lists for discrepancies')
    parser.add_argument('--active', '-a', 
                      help='Path to active courses Excel file',
                      default=os.getenv('ACTIVE_COURSES_PATH'))
    parser.add_argument('--corrected', '-c',
                      help='Path to corrected courses CSV file',
                      default=os.getenv('CORRECTED_COURSES_PATH'))
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    # If arguments weren't provided via command line or environment variables
    if not args.active or not args.corrected:
        print("Please provide the file paths using one of these methods:")
        print("\n1. Command line arguments:")
        print("   python data.py -a path/to/active_courses.xlsx -c path/to/corrected_courses.csv")
        print("\n2. Environment variables:")
        print("   Set ACTIVE_COURSES_PATH and CORRECTED_COURSES_PATH")
        print("\n3. Place your files in the current directory with these names:")
        
        # Default to files in current directory if they exist
        if not args.active and Path('Active Courses 10-1-24.xlsx').exists():
            args.active = 'Active Courses 10-1-24.xlsx'
        if not args.corrected and Path('final_fully_corrected_courses.csv').exists():
            args.corrected = 'final_fully_corrected_courses.csv'
        
        if not args.active or not args.corrected:
            sys.exit(1)
    
    try:
        comparator = CourseComparator(args.active, args.corrected)
        comparator.run_analysis()
        
    except FileNotFoundError as e:
        print(f"\nError: Could not find file: {e.filename}")
        print("Please check if the file paths are correct.")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        print("Please check your file paths and ensure both files exist.")

if __name__ == "__main__":
    main()