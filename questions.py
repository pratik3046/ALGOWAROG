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

QUESTIONS =[
    {
        'title': 'Power Level Tracker',
        'description': 'In the world of "Dragon Ball", scouts measure the power level of fighters. You are tasked with calculating the "Total Team Aura". The Aura is calculated by summing up the power levels of all fighters in a list. However, if a fighter’s power level is strictly greater than 9000, their power is so immense that it contributes double its value to the total aura.',
        'input_format': 'A single line of space-separated integers representing power levels.',
        'output_format': 'A single integer representing the Total Team Aura.',
        'constraints': '1 ≤ levels.length ≤ 1000, 1 ≤ levels[i] ≤ 10^5',
        'function_name': 'calculateAura',
        'parameters': ['levels: List[int]'],
        'return_type': 'int',
        'sample_cases': [
            {'input': '8000 9001 100', 'output': '26102'},
            {'input': '1000 2000', 'output': '3000'}
        ],
        'test_cases': [
            {'input': '8000 9001 100', 'output': '26102'},
            {'input': '1000 2000', 'output': '3000'},
            {'input': '9000 9000', 'output': '18000'},
            {'input': '9001', 'output': '18002'},
            {'input': '10000 10000', 'output': '40000'}
        ]
    },
    {
        'title': 'Uchiha Mirror String',
        'description': 'The Uchiha clan uses a secret "Mirror Jutsu". A scroll is considered a "Success" only if the string written on it is a Mirror Palindrome. A Mirror Palindrome is a string that reads the same forwards and backwards (a palindrome) AND has an even number of characters. If it meets both criteria, return "Success", otherwise return "Failure".',
        'input_format': 'A single string S containing only lowercase letters.',
        'output_format': 'The string "Success" or "Failure".',
        'constraints': '1 ≤ |S| ≤ 1000',
        'function_name': 'mirrorJutsu',
        'parameters': ['s: str'],
        'return_type': 'str',
        'sample_cases': [
            {'input': 'abba', 'output': 'Success'},
            {'input': 'aba', 'output': 'Failure'}
        ],
        'test_cases': [
            {'input': 'abba', 'output': 'Success'},
            {'input': 'aba', 'output': 'Failure'},
            {'input': 'noon', 'output': 'Success'},
            {'input': 'racecar', 'output': 'Failure'},
            {'input': 'codeedoc', 'output': 'Success'}
        ]
    },
    {
        'title': 'Hokage Election',
        'description': 'The Village Hidden in the Leaves is electing a new Hokage. Count the votes and find the winner (the name appearing most frequently). If there is a tie for the most votes, the election is inconclusive; return "Re-vote".',
        'input_format': 'A single line of space-separated strings (names).',
        'output_format': 'The name of the winner or "Re-vote".',
        'constraints': '1 ≤ number of votes ≤ 1000',
        'function_name': 'electHokage',
        'parameters': ['votes: List[str]'],
        'return_type': 'str',
        'sample_cases': [
            {'input': 'Naruto Kakashi Naruto', 'output': 'Naruto'},
            {'input': 'Naruto Sasuke', 'output': 'Re-vote'}
        ],
        'test_cases': [
            {'input': 'Naruto Kakashi Naruto', 'output': 'Naruto'},
            {'input': 'Naruto Sasuke', 'output': 'Re-vote'},
            {'input': 'Minato Minato Tobirama', 'output': 'Minato'},
            {'input': 'A B C', 'output': 'Re-vote'},
            {'input': 'Gaara Gaara Gaara', 'output': 'Gaara'}
        ]
    },
    {
        'title': 'Shinkansen Ticket Pricing',
        'description': 'Base cost: 100 Yen/KM. If distance > 500 KM, apply 10% discount to total. If passenger is a "Student", apply an additional 20% discount on the remaining price.',
        'input_format': 'First line: Integer distance. Second line: String status ("Student" or "Normal").',
        'output_format': 'Final price as a float.',
        'constraints': '1 ≤ dist ≤ 5000',
        'function_name': 'ticketPrice',
        'parameters': ['dist: int', 'status: str'],
        'return_type': 'float',
        'sample_cases': [
            {'input': '600\nStudent', 'output': '43200.0'},
            {'input': '100\nNormal', 'output': '10000.0'}
        ],
        'test_cases': [
            {'input': '600\nStudent', 'output': '43200.0'},
            {'input': '100\nNormal', 'output': '10000.0'},
            {'input': '500\nNormal', 'output': '50000.0'},
            {'input': '100\nStudent', 'output': '8000.0'},
            {'input': '1000\nNormal', 'output': '90000.0'}
        ]
    },
   {
    'title': 'The Lantern Festival',
    'description': 'During the Obon festival in Japan, families release paper lanterns into a river. You are helping organize a festival where lanterns are released in "waves". \n\nIn the first wave, X lanterns are released. Every subsequent wave has D more lanterns than the wave before it. Given the initial number of lanterns (X), the increase per wave (D), and the total number of waves (N), calculate the total number of lanterns floating in the river after all waves are released.',
    'input_format': 'Three space-separated integers: X (initial lanterns), D (increase per wave), and N (total waves).',
    'output_format': 'A single integer representing the total count of lanterns.',
    'constraints': '1 ≤ X, D ≤ 100, 1 ≤ N ≤ 50',
    'function_name': 'totalLanterns',
    'parameters': ['x: int', 'd: int', 'n: int'],
    'return_type': 'int',
    'sample_cases': [
        {'input': '10 5 3', 'output': '45'},
        {'input': '5 2 4', 'output': '32'}
    ],
    'test_cases': [
        {'input': '10 5 3', 'output': '45'}, # 10 + 15 + 20
        {'input': '5 2 4', 'output': '32'}, # 5 + 7 + 9 + 11
        {'input': '1 1 1', 'output': '1'},
        {'input': '100 0 10', 'output': '1000'},
        {'input': '10 10 5', 'output': '150'}
    ]
},
    {
        'title': 'Haiku Syllable Check',
        'description': 'Validate a Haiku based on syllable counts. Pattern must be exactly 5-7-5.',
        'input_format': 'Three space-separated integers representing syllable counts for lines 1, 2, and 3.',
        'output_format': '"Valid" or "Invalid".',
        'constraints': '1 ≤ syllables ≤ 20',
        'function_name': 'checkHaiku',
        'parameters': ['a: int', 'b: int', 'c: int'],
        'return_type': 'str',
        'sample_cases': [
            {'input': '5 7 5', 'output': 'Valid'},
            {'input': '5 6 5', 'output': 'Invalid'}
        ],
        'test_cases': [
            {'input': '5 7 5', 'output': 'Valid'},
            {'input': '5 6 5', 'output': 'Invalid'},
            {'input': '7 5 5', 'output': 'Invalid'},
            {'input': '5 7 6', 'output': 'Invalid'},
            {'input': '4 7 5', 'output': 'Invalid'}
        ]
    },
    {
        'title': 'Tea Ceremony Temperature',
        'description': 'Matcha brewing range is [75, 85] inclusive. Count how many temperatures in a list are perfect.',
        'input_format': 'Space-separated integers representing temperatures.',
        'output_format': 'Integer count of perfect temperatures.',
        'constraints': '1 ≤ number of temps ≤ 1000',
        'function_name': 'teaRange',
        'parameters': ['temps: List[int]'],
        'return_type': 'int',
        'sample_cases': [
            {'input': '70 80 82 90', 'output': '2'},
            {'input': '75 85', 'output': '2'}
        ],
        'test_cases': [
            {'input': '70 80 82 90', 'output': '2'},
            {'input': '75 85', 'output': '2'},
            {'input': '74 86', 'output': '0'},
            {'input': '80 80 80', 'output': '3'},
            {'input': '10 20 100', 'output': '0'}
        ]
    },
    {
        'title': 'Sumo Weight Class',
        'description': 'Find wrestlers qualifying for Heavyweight (>150kg). Return their weights as a space-separated string.',
        'input_format': 'Space-separated integers representing weights.',
        'output_format': 'Space-separated integers of heavyweights.',
        'constraints': '1 ≤ number of wrestlers ≤ 1000',
        'function_name': 'sumoFilter',
        'parameters': ['weights: List[int]'],
        'return_type': 'str',
        'sample_cases': [
            {'input': '140 160 180', 'output': '160 180'},
            {'input': '150 151', 'output': '151'}
        ],
        'test_cases': [
            {'input': '140 160 180', 'output': '160 180'},
            {'input': '150 151', 'output': '151'},
            {'input': '120 130', 'output': ''},
            {'input': '200', 'output': '200'},
            {'input': '160 140 170', 'output': '160 170'}
        ]
    },
    {
        'title': 'Sudoku Row Validator',
        'description': 'Check if a row (9 integers) contains all digits from 1 to 9 exactly once.',
        'input_format': 'Nine space-separated integers.',
        'output_format': '"Yes" or "No".',
        'constraints': 'All integers are 0-9.',
        'function_name': 'validSudokuRow',
        'parameters': ['row: List[int]'],
        'return_type': 'str',
        'sample_cases': [
            {'input': '1 2 3 4 5 6 7 8 9', 'output': 'Yes'},
            {'input': '1 1 2 3 4 5 6 7 8', 'output': 'No'}
        ],
        'test_cases': [
            {'input': '1 2 3 4 5 6 7 8 9', 'output': 'Yes'},
            {'input': '1 1 2 3 4 5 6 7 8', 'output': 'No'},
            {'input': '9 8 7 6 5 4 3 2 1', 'output': 'Yes'},
            {'input': '1 2 3 4 5 6 7 8 0', 'output': 'No'},
            {'input': '5 3 4 6 7 8 9 1 2', 'output': 'Yes'}
        ]
    },
    {
        'title': 'Yen Banknotes',
        'description': 'Minimum number of 1000-Yen notes to pay an amount N.',
        'input_format': 'A single integer N.',
        'output_format': 'Integer number of notes.',
        'constraints': '1 ≤ N ≤ 10^6',
        'function_name': 'yenNotes',
        'parameters': ['n: int'],
        'return_type': 'int',
        'sample_cases': [
            {'input': '2500', 'output': '3'},
            {'input': '5000', 'output': '5'}
        ],
        'test_cases': [
            {'input': '2500', 'output': '3'},
            {'input': '5000', 'output': '5'},
            {'input': '100', 'output': '1'},
            {'input': '1001', 'output': '2'},
            {'input': '999', 'output': '1'}
        ]
    },
    {
        'title': 'Kabuki Mask Replace',
        'description': 'Replace "Red" with "Hero" and "Blue" with "Villain" in a string.',
        'input_format': 'A string containing words "Red" or "Blue".',
        'output_format': 'The modified string.',
        'constraints': '1 ≤ string length ≤ 1000',
        'function_name': 'maskReplace',
        'parameters': ['s: str'],
        'return_type': 'str',
        'sample_cases': [
            {'input': 'Red enters Blue', 'output': 'Hero enters Villain'},
            {'input': 'Blue Red', 'output': 'Villain Hero'}
        ],
        'test_cases': [
            {'input': 'Red enters Blue', 'output': 'Hero enters Villain'},
            {'input': 'Blue Red', 'output': 'Villain Hero'},
            {'input': 'The Red mask', 'output': 'The Hero mask'},
            {'input': 'Nothing', 'output': 'Nothing'},
            {'input': 'RedRedBlue', 'output': 'HeroHeroVillain'}
        ]
    },
    {
        'title': 'Bento Calories',
        'description': 'Rice=200, Fish=150, Veggies=50. Calculate total calories.',
        'input_format': 'Three space-separated integers (Rice, Fish, Veggies).',
        'output_format': 'Total calories as an integer.',
        'constraints': '0 ≤ servings ≤ 100',
        'function_name': 'bentoCal',
        'parameters': ['r: int', 'f: int', 'v: int'],
        'return_type': 'int',
        'sample_cases': [
            {'input': '2 1 3', 'output': '700'},
            {'input': '1 0 0', 'output': '200'}
        ],
        'test_cases': [
            {'input': '2 1 3', 'output': '700'},
            {'input': '1 0 0', 'output': '200'},
            {'input': '0 1 0', 'output': '150'},
            {'input': '0 0 5', 'output': '250'},
            {'input': '10 10 10', 'output': '4000'}
        ]
    },
    {
        'title': 'Peak of Mt. Fuji',
        'description': 'Find the index of an element strictly greater than its neighbors.',
        'input_format': 'Space-separated integers representing heights.',
        'output_format': 'The integer index of the peak.',
        'constraints': '3 ≤ number of elements ≤ 1000',
        'function_name': 'findPeak',
        'parameters': ['heights: List[int]'],
        'return_type': 'int',
        'sample_cases': [
            {'input': '1 2 5 3 1', 'output': '2'},
            {'input': '10 20 15', 'output': '1'}
        ],
        'test_cases': [
            {'input': '1 2 5 3 1', 'output': '2'},
            {'input': '10 20 15', 'output': '1'},
            {'input': '1 5 2', 'output': '1'},
            {'input': '100 500 100', 'output': '1'},
            {'input': '1 2 3 4 5 4', 'output': '4'}
        ]
    },
    {
        'title': 'Samurai Duel',
        'description': 'Compare scores round by round. Most round wins takes the duel.',
        'input_format': 'First line: scores for Samurai A. Second line: scores for Samurai B.',
        'output_format': '"A", "B", or "Tie".',
        'constraints': '1 ≤ rounds ≤ 100',
        'function_name': 'samuraiWinner',
        'parameters': ['a: List[int]', 'b: List[int]'],
        'return_type': 'str',
        'sample_cases': [
            {'input': '10 20\n5 25', 'output': 'Tie'},
            {'input': '30 40\n10 20', 'output': 'A'}
        ],
        'test_cases': [
            {'input': '10 20\n5 25', 'output': 'Tie'},
            {'input': '30 40\n10 20', 'output': 'A'},
            {'input': '10 10\n20 20', 'output': 'B'},
            {'input': '50\n40', 'output': 'A'},
            {'input': '5 5 5\n5 5 5', 'output': 'Tie'}
        ]
    },
    {
        'title': 'Kimono Pattern',
        'description': 'Check if array follows a 2-element repeating pattern [a, b, a, b...].',
        'input_format': 'Space-separated integers.',
        'output_format': '"Yes" or "No".',
        'constraints': '2 ≤ length ≤ 1000 (even length).',
        'function_name': 'isPatternValid',
        'parameters': ['pattern: List[int]'],
        'return_type': 'str',
        'sample_cases': [
            {'input': '1 2 1 2', 'output': 'Yes'},
            {'input': '1 2 1 3', 'output': 'No'}
        ],
        'test_cases': [
            {'input': '1 2 1 2', 'output': 'Yes'},
            {'input': '1 2 1 3', 'output': 'No'},
            {'input': '5 5 5 5', 'output': 'Yes'},
            {'input': '1 2 1 2 1 2', 'output': 'Yes'},
            {'input': '1 2 3 4', 'output': 'No'}
        ]
    },
    {
        'title': 'Kanji Digit Sum',
        'description': 'Convert strings "One", "Two", "Three" to 1, 2, 3 and return total sum.',
        'input_format': 'Space-separated strings ("One", "Two", "Three").',
        'output_format': 'Total sum as an integer.',
        'constraints': '1 ≤ list length ≤ 100',
        'function_name': 'kanjiSum',
        'parameters': ['s: List[str]'],
        'return_type': 'int',
        'sample_cases': [
            {'input': 'One Two Three', 'output': '6'},
            {'input': 'One One One', 'output': '3'}
        ],
        'test_cases': [
            {'input': 'One Two Three', 'output': '6'},
            {'input': 'One One One', 'output': '3'},
            {'input': 'Three Three', 'output': '6'},
            {'input': 'Two', 'output': '2'},
            {'input': 'Three Two One', 'output': '6'}
        ]
    },
    {
        'title': 'Manga Chapter Sort',
        'description': 'Sort volume strings like "Vol10", "Vol2" in correct numeric order.',
        'input_format': 'Space-separated strings ("VolX").',
        'output_format': 'Space-separated sorted strings.',
        'constraints': '1 ≤ number of volumes ≤ 100',
        'function_name': 'sortManga',
        'parameters': ['vols: List[str]'],
        'return_type': 'str',
        'sample_cases': [
            {'input': 'Vol10 Vol1 Vol2', 'output': 'Vol1 Vol2 Vol10'},
            {'input': 'Vol5 Vol3 Vol1', 'output': 'Vol1 Vol3 Vol5'}
        ],
        'test_cases': [
            {'input': 'Vol10 Vol1 Vol2', 'output': 'Vol1 Vol2 Vol10'},
            {'input': 'Vol5 Vol3 Vol1', 'output': 'Vol1 Vol3 Vol5'},
            {'input': 'Vol2 Vol20 Vol11', 'output': 'Vol2 Vol11 Vol20'},
            {'input': 'Vol1', 'output': 'Vol1'},
            {'input': 'Vol100 Vol10 Vol1', 'output': 'Vol1 Vol10 Vol100'}
        ]
    },
    {
        'title': 'Hidden Leaf Cipher',
        'description': 'Shift every character in a string by +1 in the ASCII table.',
        'input_format': 'A single string S.',
        'output_format': 'The encoded string.',
        'constraints': '1 ≤ |S| ≤ 1000',
        'function_name': 'leafCipher',
        'parameters': ['s: str'],
        'return_type': 'str',
        'sample_cases': [
            {'input': 'abc', 'output': 'bcd'},
            {'input': 'hello', 'output': 'ifmmp'}
        ],
        'test_cases': [
            {'input': 'abc', 'output': 'bcd'},
            {'input': 'hello', 'output': 'ifmmp'},
            {'input': 'ninja', 'output': 'ojokb'},
            {'input': 'z', 'output': '{'},
            {'input': 'ABC', 'output': 'BCD'}
        ]
    },
    {
        'title': 'Ninja Distance',
        'description': 'Calculate Manhattan Distance: |x1 - x2| + |y1 - y2| between two points.',
        'input_format': 'Four space-separated integers x1 y1 x2 y2.',
        'output_format': 'The integer distance.',
        'constraints': '-1000 ≤ coordinates ≤ 1000',
        'function_name': 'ninjaDist',
        'parameters': ['x1: int', 'y1: int', 'x2: int', 'y2: int'],
        'return_type': 'int',
        'sample_cases': [
            {'input': '0 0 3 4', 'output': '7'},
            {'input': '1 1 1 1', 'output': '0'}
        ],
        'test_cases': [
            {'input': '0 0 3 4', 'output': '7'},
            {'input': '1 1 1 1', 'output': '0'},
            {'input': '10 5 12 7', 'output': '4'},
            {'input': '0 0 0 5', 'output': '5'},
            {'input': '-1 -1 1 1', 'output': '4'}
        ]
    },
    {
        'title': 'Go Board Check',
        'description': 'Determine if an (x, y) coordinate is within a 19x19 grid (1 to 19).',
        'input_format': 'Two space-separated integers x and y.',
        'output_format': '"Inside" or "Outside".',
        'constraints': '0 ≤ x, y ≤ 50',
        'function_name': 'goBoardCheck',
        'parameters': ['x: int', 'y: int'],
        'return_type': 'str',
        'sample_cases': [
            {'input': '10 10', 'output': 'Inside'},
            {'input': '20 5', 'output': 'Outside'}
        ],
        'test_cases': [
            {'input': '10 10', 'output': 'Inside'},
            {'input': '20 5', 'output': 'Outside'},
            {'input': '1 1', 'output': 'Inside'},
            {'input': '19 19', 'output': 'Inside'},
            {'input': '0 10', 'output': 'Outside'}
        ]
    },
    {
        'title': 'Marathon End',
        'description': 'Start 10:00 AM. Each episode is 24 minutes. Calculate finish time (HH:MM).',
        'input_format': 'A single integer N (episodes).',
        'output_format': 'Time string in 24hr format HH:MM.',
        'constraints': '1 ≤ N ≤ 35',
        'function_name': 'marathonEnd',
        'parameters': ['n: int'],
        'return_type': 'str',
        'sample_cases': [
            {'input': '5', 'output': '12:00'},
            {'input': '1', 'output': '10:24'}
        ],
        'test_cases': [
            {'input': '5', 'output': '12:00'},
            {'input': '1', 'output': '10:24'},
            {'input': '10', 'output': '14:00'},
            {'input': '2', 'output': '10:48'},
            {'input': '25', 'output': '20:00'}
        ]
    },
    {
        'title': 'Tokyo Time',
        'description': 'Convert UTC hour (0-23) to Tokyo Time (UTC+9). Wrap around if needed.',
        'input_format': 'An integer UTC hour.',
        'output_format': 'An integer Tokyo hour.',
        'constraints': '0 ≤ utc_h ≤ 23',
        'function_name': 'tokyoTime',
        'parameters': ['utc_h: int'],
        'return_type': 'int',
        'sample_cases': [
            {'input': '10', 'output': '19'},
            {'input': '20', 'output': '5'}
        ],
        'test_cases': [
            {'input': '10', 'output': '19'},
            {'input': '20', 'output': '5'},
            {'input': '0', 'output': '9'},
            {'input': '15', 'output': '0'},
            {'input': '23', 'output': '8'}
        ]
    },
    {
        'title': 'Tanuki Carry',
        'description': 'Pick lightest items first. How many can be carried within weight W?',
        'input_format': 'First line: space-separated weights. Second line: limit W.',
        'output_format': 'Integer count of items.',
        'constraints': '1 ≤ number of items ≤ 1000',
        'function_name': 'tanukiCarry',
        'parameters': ['items: List[int]', 'w: int'],
        'return_type': 'int',
        'sample_cases': [
            {'input': '10 20 30\n35', 'output': '2'},
            {'input': '5 5 5\n10', 'output': '2'}
        ],
        'test_cases': [
            {'input': '10 20 30\n35', 'output': '2'},
            {'input': '5 5 5\n10', 'output': '2'},
            {'input': '10 10\n5', 'output': '0'},
            {'input': '1 2 3 4 5\n15', 'output': '5'},
            {'input': '100\n50', 'output': '0'}
        ]
    },
    {
        'title': 'Origami Square',
        'description': 'Find area of the largest possible square from a rectangular sheet W x H.',
        'input_format': 'Two space-separated integers W and H.',
        'output_format': 'Integer area of the square.',
        'constraints': '1 ≤ W, H ≤ 10^4',
        'function_name': 'maxSquare',
        'parameters': ['w: int', 'h: int'],
        'return_type': 'int',
        'sample_cases': [
            {'input': '10 15', 'output': '100'},
            {'input': '20 20', 'output': '400'}
        ],
        'test_cases': [
            {'input': '10 15', 'output': '100'},
            {'input': '20 20', 'output': '400'},
            {'input': '5 2', 'output': '4'},
            {'input': '1 100', 'output': '1'},
            {'input': '7 8', 'output': '49'}
        ]
    },
    {
        'title': 'Hanabi Sequence',
        'description': 'Given two fired fireworks (Red, Green, Blue), find the missing color.',
        'input_format': 'Two space-separated strings.',
        'output_format': 'The missing color string.',
        'constraints': 'Input is always two different valid colors.',
        'function_name': 'missingColor',
        'parameters': ['colors: List[str]'],
        'return_type': 'str',
        'sample_cases': [
            {'input': 'Red Green', 'output': 'Blue'},
            {'input': 'Blue Red', 'output': 'Green'}
        ],
        'test_cases': [
            {'input': 'Red Green', 'output': 'Blue'},
            {'input': 'Blue Red', 'output': 'Green'},
            {'input': 'Green Blue', 'output': 'Red'},
            {'input': 'Red Blue', 'output': 'Green'},
            {'input': 'Green Red', 'output': 'Blue'}
        ]
    },
    {
        'title': 'Sake Dilution',
        'description': 'Calculate new alcohol % of 15% Sake mixed with water.',
        'input_format': 'Two space-separated integers (Sake volume V, Water volume W).',
        'output_format': 'Floating point alcohol percentage.',
        'constraints': '1 ≤ V ≤ 1000, 0 ≤ W ≤ 1000',
        'function_name': 'sakePercent',
        'parameters': ['v: int', 'w: int'],
        'return_type': 'float',
        'sample_cases': [
            {'input': '100 100', 'output': '7.5'},
            {'input': '100 0', 'output': '15.0'}
        ],
        'test_cases': [
            {'input': '100 100', 'output': '7.5'},
            {'input': '100 0', 'output': '15.0'},
            {'input': '0 100', 'output': '0.0'},
            {'input': '50 150', 'output': '3.75'},
            {'input': '200 100', 'output': '10.0'}
        ]
    },
    {
        'title': 'Shrine Fortune',
        'description': 'Prime number draws "Great Blessing", Non-prime Even draws "Small Blessing", else "Future Blessing".',
        'input_format': 'A single integer N.',
        'output_format': 'A string fortune description.',
        'constraints': '1 ≤ N ≤ 1000',
        'function_name': 'omikuji',
        'parameters': ['n: int'],
        'return_type': 'str',
        'sample_cases': [
            {'input': '7', 'output': 'Great Blessing'},
            {'input': '4', 'output': 'Small Blessing'}
        ],
        'test_cases': [
            {'input': '7', 'output': 'Great Blessing'},
            {'input': '4', 'output': 'Small Blessing'},
            {'input': '9', 'output': 'Future Blessing'},
            {'input': '2', 'output': 'Great Blessing'},
            {'input': '10', 'output': 'Small Blessing'}
        ]
    },
    {
        'title': 'Daruma Balance',
        'description': 'Check if the sum of the first half of an array equals the second half.',
        'input_format': 'Space-separated integers (even length).',
        'output_format': '"Balanced" or "Not Balanced".',
        'constraints': '2 ≤ length ≤ 100',
        'function_name': 'darumaBalance',
        'parameters': ['weights: List[int]'],
        'return_type': 'str',
        'sample_cases': [
            {'input': '1 2 2 1', 'output': 'Balanced'},
            {'input': '1 1 2 2', 'output': 'Not Balanced'}
        ],
        'test_cases': [
            {'input': '1 2 2 1', 'output': 'Balanced'},
            {'input': '1 1 2 2', 'output': 'Not Balanced'},
            {'input': '10 10', 'output': 'Balanced'},
            {'input': '5 0 0 5', 'output': 'Balanced'},
            {'input': '1 2 3 4', 'output': 'Not Balanced'}
        ]
    },
    {
        'title': 'Onsen Capacity',
        'description': 'Given capacity C, hourly arrivals X and departures Y, check if limit is exceeded within H hours.',
        'input_format': 'Four space-separated integers C X Y H.',
        'output_format': '"Yes" or "No".',
        'constraints': '1 ≤ C, X, Y, H ≤ 1000',
        'function_name': 'onsenCheck',
        'parameters': ['c: int', 'x: int', 'y: int', 'h: int'],
        'return_type': 'str',
        'sample_cases': [
            {'input': '10 5 2 3', 'output': 'No'},
            {'input': '10 5 2 5', 'output': 'Yes'}
        ],
        'test_cases': [
            {'input': '10 5 2 3', 'output': 'No'},
            {'input': '10 5 2 5', 'output': 'Yes'},
            {'input': '100 10 10 5', 'output': 'No'},
            {'input': '20 10 5 2', 'output': 'No'},
            {'input': '20 10 5 5', 'output': 'Yes'}
        ]
    },
    {
        'title': 'Katana Sharpness',
        'description': 'Final sharpness = Initial S - (Hits H / 10). Minimum result is 0.',
        'input_format': 'Two space-separated integers H and S.',
        'output_format': 'Integer final sharpness.',
        'constraints': '0 ≤ H, S ≤ 1000',
        'function_name': 'katanaSharp',
        'parameters': ['h: int', 's: int'],
        'return_type': 'int',
        'sample_cases': [
            {'input': '25 10', 'output': '8'},
            {'input': '5 10', 'output': '10'}
        ],
        'test_cases': [
            {'input': '25 10', 'output': '8'},
            {'input': '5 10', 'output': '10'},
            {'input': '100 5', 'output': '0'},
            {'input': '50 10', 'output': '5'},
            {'input': '9 1', 'output': '1'}
        ]
    }
]