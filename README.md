# Langmaker

Langmaker is a Python-based tool for generating custom programming languages. It allows you to create personalized languages with unique syntax and features, making programming more fun and creative.

## Features

- Generate custom programming languages based on JSON configuration files
- Customize language syntax, keywords, and behavior
- Create interpreters for your custom languages
- Generate example programs in your new language
- Produce README files for each generated language

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/Bhavya/langmaker.git
   ```
2. Navigate to the langmaker directory:
   ```
   cd langmaker
   ```

## Usage

1. Create a JSON configuration file for your language. For example, `my_lang_config.json`:

   ```json
   {
     "language_name": "MYLANG",
     "file_extension": ".ml",
     "command_name": "mylangrun",
     "comment_prefix": "COMMENT",
     "command_prefix": "MY",
     "case_sensitive": false,
     "enforce_uppercase_comments": true,
     "enforce_uppercase_code": true,
     "type_prefixes": {
       "integer": "MYINT",
       "float": "MYFLOAT",
       "string": "MYSTRING"
     },
     "block_end": "MYEND",
     "true_value": "YES",
     "false_value": "NO"
   }
   ```

2. Run the langmaker script:
   ```
   python langmaker.py my_lang_config.json
   ```

3. Your new language will be generated in the `langs/mylang/` directory (note the lowercase directory name).

## Generated Language Structure

For each language you generate, langmaker creates the following structure:

```
langs/
└── mylang/
    ├── lib/
    │   └── mylang.py
    ├── arithmetic.ml
    ├── boolean_logic.ml
    ├── server.ml
    ├── string_manipulation.ml
    ├── README.md
    └── mylangrun
```

- `lib/mylang.py`: The interpreter for your language
- `*.ml`: Example programs in your new language
- `README.md`: Documentation for your language
- `mylangrun`: Shell script to run programs in your language

## Running Programs in Your New Language

To run a program in your newly created language:

```
./langs/mylang/mylangrun program_name.ml
```

Replace `mylang` with your lowercase language name and `program_name.ml` with your file name.

## Customizing Your Language

You can customize various aspects of your language by modifying the JSON configuration file. Here are some key fields:

- `language_name`: The name of your language
- `file_extension`: The file extension for programs in your language
- `command_name`: The command used to run programs in your language
- `comment_prefix`: The prefix used for comments
- `command_prefix`: The prefix used for built-in commands
- `type_prefixes`: Prefixes for different data types
- `true_value` and `false_value`: Custom representations for boolean values

## Example Programs

### Hello World

Here's a simple "Hello World" program in the MYLANG language (assuming the configuration above):

```
COMMENT This is a hello world program in MYLANG

MYSTRING greeting = "Hello, World!"
MYPRINT(greeting)
```

### Arithmetic Operations

```
COMMENT Arithmetic operations in MYLANG

MYINT a = 10
MYINT b = 5

MYPRINT(MYSTRING "Sum:", a + b)
MYPRINT(MYSTRING "Difference:", a - b)
MYPRINT(MYSTRING "Product:", a * b)
MYPRINT(MYSTRING "Quotient:", a / b)
```

### Boolean Logic

```
COMMENT Boolean logic in MYLANG

MYIF YES:
    MYPRINT(MYSTRING "This is true!")
MYEND

MYIF NO:
    MYPRINT(MYSTRING "This will not be printed")
MYELSE:
    MYPRINT(MYSTRING "This is false!")
MYEND
```

Save these examples with the `.ml` extension and run them using the `mylangrun` script.

## Troubleshooting

If you encounter any issues while generating or running your custom language, please check the following:

1. Ensure your JSON configuration file is valid and contains all required fields.
2. Check that you're running the langmaker script from the correct directory.
3. Verify that the generated language files have the correct permissions.

If problems persist, please open an issue on the GitHub repository with a detailed description of the error and your configuration file.

## Contributing

Contributions to langmaker are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to all contributors who have helped shape this project
- Inspired by the joy of creating and learning new programming languages

Happy language making!
