#!/usr/bin/php
<?php
    class Arguments {
        public $help         = FALSE;
        public $input        = "php://stdin";
        public $output       = "php://stout";
        public $invalid_char = "-";
        public $xml_header   = TRUE;
        public $root_element = NULL;
        public $arr_name     = "array";
        public $item_name    = "item";
        public $str2element  = FALSE;
        public $itm2element  = FALSE;
        public $literal      = FALSE;
        public $decode       = FALSE;
        public $arr_size     = FALSE;
        public $idx_item     = FALSE;
        public $idx_start    = 1;
        public $add_types    = FALSE;

        private $set_input   = FALSE;
        private $set_output  = FALSE;
        private $set_inv     = FALSE;
        private $set_start   = FALSE;
        private $set_arr     = FALSE;
        private $set_item    = FALSE;

        public function __construct($arguments) {
            foreach ($arguments as $arg) {
                if ($arg == "--help" and $this->help == FALSE) {
                    $this->help = TRUE;
                }
                elseif ($arg == "-s" and $this->str2element == FALSE) {
                    $this->str2element = TRUE;
                }
                elseif ($arg == "-i" and $this->itm2element == FALSE) {
                    $this->itm2element = TRUE;
                }
                elseif ($arg == "-l" and $this->literal == FALSE) {
                    $this->literal = TRUE;
                }
                elseif ($arg == "-c" and $this->decode == FALSE) {
                    $this->decode = TRUE;
                }
                elseif ($arg == "-n" and $this->xml_header == TRUE) {
                    $this->xml_header = FALSE;
                }
                elseif (($arg == "-a" or $arg == "--array-size") and $this->arr_size == FALSE) {
                    $this->arr_size = TRUE;
                }
                elseif (($arg == "-t" or $arg == "--index-items") and $this->idx_item == FALSE) {
                    $this->idx_item = TRUE;
                }
                elseif ($arg == "--types" and $this->add_types == FALSE) {
                    $this->add_types = TRUE;
                }
                elseif (preg_match("/^--input=.+/", $arg) and $this->set_input == FALSE) {
                    $this->input     = substr($arg, 8);
                    $this->set_input = TRUE;
                }
                elseif (preg_match("/^--output=.+/", $arg) and $this->set_output == FALSE) {
                    $this->output     = substr($arg, 9);
                    $this->set_output = TRUE;
                }
                elseif (preg_match("/^-h=.+/", $arg) and $this->set_inv == FALSE) {
                    $this->invalid_char = substr($arg, 3);
                    $this->set_inv      = TRUE;
                }
                elseif (preg_match("/^-r=.+/", $arg) and $this->root_element == NULL) {
                    $this->root_element = substr($arg, 3);
                }
                elseif (preg_match("/^--start=.+/", $arg) and $this->set_start == FALSE) {
                    $tmp = substr($arg, 8);
                    if (is_int($tmp) and (int)$tmp >= 0) {
                        $this->idx_start = (int)$tmp;
                        $this->set_start = TRUE;
                    }
                    else {
                        err("Invalid value of --start=n argument", 1);
                    }
                }
                elseif (preg_match("/^--array-name=.+/", $arg) and $this->set_arr == FALSE) {
                    $this->root_element = substr($arg, 13);
                    $this->set_arr      = TRUE;
                }
                elseif (preg_match("/^--item-name=.+/", $arg) and $this->set_item == FALSE) {
                    $this->root_element = substr($arg, 12);
                    $this->set_item     = TRUE;
                }
                else {
                    err("Invalid use of program arguments", 1);
                }
            }
        }

        public function check_arguments() {
            if ($this->help == TRUE) {
                $this->print_help();
            }
            if ($this->idx_item == FALSE and $this->set_start == TRUE) {
                err("Invalid use of program arguments", 1);
            }
            //TODO
        }

        /**
         * Print manual page on standart output and exit program with return code 0
         */
        private function print_help() {
            echo    "Usage: php ./proj1 ",
                    "[--input=filename --output=filename -s -i -c -n --help -h=subst -r=root-element -a -t --start --types --array-name=array-element --item-name=item-element]\n",
                    "Created by Matejka Jiri (xmatej52)",
                    "-s                         values of type string will be transformed to text elements\n",
                    "-i                         TODO",
                    "-l                         values of true, false and null will be transfored to elements\n",
                    "-c                         Try to eliminate invalid characters\n",
                    "-n                         Will not generate XML header\n",
                    "--help                     Print this message\n",
                    "--input=filename           Input JSON file\n",
                    "--output=filename          Output XML file\n",
                    "-h=subst                   Replacing invalid characters by 'subst'\n",
                    "-r=root-element            Name of root element\n",
                    "-a, --array-size           Size of array will be added\n",
                    "-t, --index-items          Index will be aded for items of array\n",
                    "--start=n                  Starting index while indexing items in array\n",
                    "--types                    Types of values will be added\n",
                    "--array-name=array-element Name of array element\n",
                    "--item-name=item-element   Name of array item element\n";
                    exit(0);
        }
    }

    /**
     * Writes error message on standart error output and exit program
     * @param  string $str error message
     * @param  [type] $err return code
     */
    function err($str, $err) {
        fwrite(STDERR, $str . "\n");
        exit($err);
    }

    function read_input(Arguments $args) {
        try {
            $input = file_get_contents($args->input);
        } catch (Exception $e) {
            err("Can't open '$args->input' as input file.", 2);
        }
        $json = json_decode($input, true);
        if ($json == NULL) {
            err("Can't decode input data", 4);
        }
        return $json;
    }

    // source: http://stackoverflow.com/questions/1241728/can-i-try-catch-a-warning
    set_error_handler(function($errno, $errstr, $errfile, $errline, array $errcontext) {
        if (0 === error_reporting()) {
            return false;
        }
        throw new ErrorException($errstr, 0, $errno, $errfile, $errline);
    });

    unset($argv[0]);
    $args = new Arguments($argv);
    $args->check_arguments();
//    print_r(get_object_vars($args));
    $json = read_input($args);
    var_dump($json);
?>
