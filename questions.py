"""
Competitive Programming Questions for Code Battle Tournament
Each question has:
- 'title': Problem title
- 'description': Problem statement
- 'input_format': Description of input format
- 'output_format': Description of output format
- 'constraints': Problem constraints
- 'test_cases': List of {'input': str, 'output': str} for validation
- 'sample_cases': Visible examples for contestants
"""

QUESTIONS = [
    {
        'title': 'Two Sum',
        'description': 'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. You may assume that each input would have exactly one solution, and you may not use the same element twice.',
        'input_format': 'First line: array of integers (space-separated)\nSecond line: target integer',
        'output_format': 'Two space-separated integers: the indices of the two numbers',
        'constraints': '2 ≤ nums.length ≤ 10^4\n-10^9 ≤ nums[i] ≤ 10^9\n-10^9 ≤ target ≤ 10^9\nOnly one valid answer exists.',
        'function_name': 'twoSum',
        'parameters': ['nums: List[int]', 'target: int'],
        'return_type': 'List[int]',
        'sample_cases': [
            {'input': '2 7 11 15\n9', 'output': '0 1'},
            {'input': '3 2 4\n6', 'output': '1 2'},
            {'input': '3 3\n6', 'output': '0 1'}
        ],
        'test_cases': [
            {'input': '2 7 11 15\n9', 'output': '0 1'},
            {'input': '3 2 4\n6', 'output': '1 2'},
            {'input': '3 3\n6', 'output': '0 1'},
            {'input': '1 2 3 4 5\n9', 'output': '3 4'},
            {'input': '5 5 5 5\n10', 'output': '0 1'}
        ]
    },
    {
        'title': 'Reverse String',
        'description': 'Write a function that reverses a string and returns the reversed string.',
        'input_format': 'A single line containing a string',
        'output_format': 'The reversed string',
        'constraints': '1 ≤ string length ≤ 1000\nString contains only printable ASCII characters.',
        'function_name': 'reverseString',
        'parameters': ['s: str'],
        'return_type': 'str',
        'sample_cases': [
            {'input': 'hello', 'output': 'olleh'},
            {'input': 'Hannah', 'output': 'hannaH'}
        ],
        'test_cases': [
            {'input': 'hello', 'output': 'olleh'},
            {'input': 'Hannah', 'output': 'hannaH'},
            {'input': 'a', 'output': 'a'},
            {'input': 'abc', 'output': 'cba'},
            {'input': 'racecar', 'output': 'racecar'}
        ]
    },
    {
        'title': 'Maximum Subarray',
        'description': 'Given an integer array nums, find the contiguous subarray (containing at least one number) which has the largest sum and return its sum.',
        'input_format': 'Space-separated integers representing the array',
        'output_format': 'Single integer: the largest sum of contiguous subarray',
        'constraints': '1 ≤ nums.length ≤ 10^5\n-10^4 ≤ nums[i] ≤ 10^4',
        'function_name': 'maxSubArray',
        'parameters': ['nums: List[int]'],
        'return_type': 'int',
        'sample_cases': [
            {'input': '-2 1 -3 4 -1 2 1 -5 4', 'output': '6'},
            {'input': '1', 'output': '1'},
            {'input': '5 4 -1 7 8', 'output': '23'}
        ],
        'test_cases': [
            {'input': '-2 1 -3 4 -1 2 1 -5 4', 'output': '6'},
            {'input': '1', 'output': '1'},
            {'input': '5 4 -1 7 8', 'output': '23'},
            {'input': '-1', 'output': '-1'},
            {'input': '-2 -1', 'output': '-1'}
        ]
    },
    {
        'title': 'Maximum of Array',
        'description': 'Given N integers, find the maximum value.',
        'input_format': 'First line: integer N\nSecond line: N space-separated integers',
        'output_format': 'Single integer: the maximum value',
        'constraints': '1 ≤ N ≤ 1000\n-10^9 ≤ each element ≤ 10^9',
        'function_name': 'findMax',
        'parameters': ['nums: List[int]'],
        'return_type': 'int',
        'sample_cases': [
            {'input': '5\n1 3 7 2 5', 'output': '7'},
            {'input': '3\n-5 -2 -8', 'output': '-2'}
        ],
        'test_cases': [
            {'input': '5\n1 3 7 2 5', 'output': '7'},
            {'input': '3\n-5 -2 -8', 'output': '-2'},
            {'input': '1\n42', 'output': '42'},
            {'input': '4\n100 200 150 180', 'output': '200'},
            {'input': '6\n-10 0 5 -3 8 2', 'output': '8'}
        ]
    },
    {
        'title': 'Even or Odd',
        'description': 'Given an integer N, determine if it is even or odd.',
        'input_format': 'A single integer N',
        'output_format': 'Print "Even" if N is even, "Odd" if N is odd',
        'constraints': '-10^9 ≤ N ≤ 10^9',
        'function_name': 'checkEvenOdd',
        'parameters': ['n: int'],
        'return_type': 'str',
        'sample_cases': [
            {'input': '4', 'output': 'Even'},
            {'input': '7', 'output': 'Odd'}
        ],
        'test_cases': [
            {'input': '4', 'output': 'Even'},
            {'input': '7', 'output': 'Odd'},
            {'input': '0', 'output': 'Even'},
            {'input': '-3', 'output': 'Odd'},
            {'input': '1000', 'output': 'Even'}
        ]
    },
    {
        'title': 'Factorial',
        'description': 'Calculate the factorial of a given non-negative integer N.',
        'input_format': 'A single integer N',
        'output_format': 'Single integer: N! (factorial of N)',
        'constraints': '0 ≤ N ≤ 12',
        'function_name': 'factorial',
        'parameters': ['n: int'],
        'return_type': 'int',
        'sample_cases': [
            {'input': '5', 'output': '120'},
            {'input': '3', 'output': '6'}
        ],
        'test_cases': [
            {'input': '5', 'output': '120'},
            {'input': '3', 'output': '6'},
            {'input': '0', 'output': '1'},
            {'input': '1', 'output': '1'},
            {'input': '4', 'output': '24'}
        ]
    },
    {
        'title': 'Prime Check',
        'description': 'Given an integer N, determine if it is a prime number. A prime number is a natural number greater than 1 that has no positive divisors other than 1 and itself.',
        'input_format': 'A single integer N',
        'output_format': 'Print "Prime" if N is prime, "Not Prime" otherwise',
        'constraints': '1 ≤ N ≤ 10^6',
        'function_name': 'isPrime',
        'parameters': ['n: int'],
        'return_type': 'str',
        'sample_cases': [
            {'input': '7', 'output': 'Prime'},
            {'input': '10', 'output': 'Not Prime'}
        ],
        'test_cases': [
            {'input': '7', 'output': 'Prime'},
            {'input': '10', 'output': 'Not Prime'},
            {'input': '2', 'output': 'Prime'},
            {'input': '1', 'output': 'Not Prime'},
            {'input': '97', 'output': 'Prime'}
        ]
    },
    {
        'title': 'Fibonacci Number',
        'description': 'Find the Nth Fibonacci number. The Fibonacci sequence is: 0, 1, 1, 2, 3, 5, 8, 13, ... where each number is the sum of the two preceding ones.',
        'input_format': 'A single integer N (0-indexed)',
        'output_format': 'The Nth Fibonacci number',
        'constraints': '0 ≤ N ≤ 30',
        'function_name': 'fibonacci',
        'parameters': ['n: int'],
        'return_type': 'int',
        'sample_cases': [
            {'input': '6', 'output': '8'},
            {'input': '10', 'output': '55'}
        ],
        'test_cases': [
            {'input': '6', 'output': '8'},
            {'input': '10', 'output': '55'},
            {'input': '0', 'output': '0'},
            {'input': '1', 'output': '1'},
            {'input': '2', 'output': '1'}
        ]
    },
    {
        'title': 'Palindrome Check',
        'description': 'Given a string S, check if it is a palindrome (reads the same forwards and backwards). Consider only alphanumeric characters and ignore case.',
        'input_format': 'A single line containing string S',
        'output_format': 'Print "Yes" if palindrome, "No" otherwise',
        'constraints': '1 ≤ |S| ≤ 1000',
        'function_name': 'isPalindrome',
        'parameters': ['s: str'],
        'return_type': 'str',
        'sample_cases': [
            {'input': 'racecar', 'output': 'Yes'},
            {'input': 'hello', 'output': 'No'}
        ],
        'test_cases': [
            {'input': 'racecar', 'output': 'Yes'},
            {'input': 'hello', 'output': 'No'},
            {'input': 'a', 'output': 'Yes'},
            {'input': 'madam', 'output': 'Yes'},
            {'input': 'python', 'output': 'No'}
        ]
    },
    {
        'title': 'Count Words',
        'description': 'Given a sentence, count the number of words in it. Words are separated by one or more spaces.',
        'input_format': 'A single line containing a sentence',
        'output_format': 'Single integer: number of words',
        'constraints': '1 ≤ length ≤ 1000',
        'function_name': 'countWords',
        'parameters': ['sentence: str'],
        'return_type': 'int',
        'sample_cases': [
            {'input': 'hello world', 'output': '2'},
            {'input': 'I love programming', 'output': '3'}
        ],
        'test_cases': [
            {'input': 'hello world', 'output': '2'},
            {'input': 'I love programming', 'output': '3'},
            {'input': 'test', 'output': '1'},
            {'input': 'a b c d e', 'output': '5'},
            {'input': 'The quick brown fox', 'output': '4'}
        ]
    },
    {
        'title': 'GCD of Two Numbers',
        'description': 'Find the Greatest Common Divisor (GCD) of two integers A and B using the Euclidean algorithm.',
        'input_format': 'Two space-separated integers A and B',
        'output_format': 'Single integer: GCD(A, B)',
        'constraints': '1 ≤ A, B ≤ 10^9',
        'function_name': 'gcd',
        'parameters': ['a: int', 'b: int'],
        'return_type': 'int',
        'sample_cases': [
            {'input': '12 8', 'output': '4'},
            {'input': '7 5', 'output': '1'}
        ],
        'test_cases': [
            {'input': '12 8', 'output': '4'},
            {'input': '7 5', 'output': '1'},
            {'input': '100 50', 'output': '50'},
            {'input': '17 19', 'output': '1'},
            {'input': '48 18', 'output': '6'}
        ]
    },
    {
        'title': 'Sum of Digits',
        'description': 'Given an integer N, find the sum of its digits.',
        'input_format': 'A single integer N',
        'output_format': 'Single integer: sum of digits',
        'constraints': '0 ≤ N ≤ 10^9',
        'function_name': 'sumOfDigits',
        'parameters': ['n: int'],
        'return_type': 'int',
        'sample_cases': [
            {'input': '123', 'output': '6'},
            {'input': '9875', 'output': '29'}
        ],
        'test_cases': [
            {'input': '123', 'output': '6'},
            {'input': '9875', 'output': '29'},
            {'input': '0', 'output': '0'},
            {'input': '7', 'output': '7'},
            {'input': '1000', 'output': '1'}
        ]
    },
    {
        'title': 'Add Two Numbers',
        'description': 'Given two integers A and B, return their sum.',
        'input_format': 'Two space-separated integers A and B',
        'output_format': 'Single integer: A + B',
        'constraints': '-10^9 ≤ A, B ≤ 10^9',
        'function_name': 'addTwoNumbers',
        'parameters': ['a: int', 'b: int'],
        'return_type': 'int',
        'sample_cases': [
            {'input': '5 3', 'output': '8'},
            {'input': '-2 7', 'output': '5'}
        ],
        'test_cases': [
            {'input': '5 3', 'output': '8'},
            {'input': '-2 7', 'output': '5'},
            {'input': '0 0', 'output': '0'},
            {'input': '100 -50', 'output': '50'},
            {'input': '-10 -20', 'output': '-30'}
        ]
    },
    {
        'title': 'Count Vowels',
        'description': 'Given a string, count the number of vowels (a, e, i, o, u) in it. Case insensitive.',
        'input_format': 'A single line containing a string',
        'output_format': 'Single integer: number of vowels',
        'constraints': '1 ≤ string length ≤ 1000',
        'function_name': 'countVowels',
        'parameters': ['s: str'],
        'return_type': 'int',
        'sample_cases': [
            {'input': 'hello', 'output': '2'},
            {'input': 'AEIOU', 'output': '5'}
        ],
        'test_cases': [
            {'input': 'hello', 'output': '2'},
            {'input': 'AEIOU', 'output': '5'},
            {'input': 'xyz', 'output': '0'},
            {'input': 'Programming', 'output': '3'},
            {'input': 'a', 'output': '1'}
        ]
    },
    {
        'title': 'Array Sum',
        'description': 'Given an array of integers, find the sum of all elements.',
        'input_format': 'First line: integer N (number of elements)\nSecond line: N space-separated integers',
        'output_format': 'Single integer: sum of all elements',
        'constraints': '1 ≤ N ≤ 1000\n-10^6 ≤ each element ≤ 10^6',
        'function_name': 'arraySum',
        'parameters': ['nums: List[int]'],
        'return_type': 'int',
        'sample_cases': [
            {'input': '5\n1 2 3 4 5', 'output': '15'},
            {'input': '3\n-1 0 1', 'output': '0'}
        ],
        'test_cases': [
            {'input': '5\n1 2 3 4 5', 'output': '15'},
            {'input': '3\n-1 0 1', 'output': '0'},
            {'input': '1\n42', 'output': '42'},
            {'input': '4\n10 -5 3 -2', 'output': '6'},
            {'input': '2\n100 200', 'output': '300'}
        ]
    }
]