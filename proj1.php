#!/usr/bin/php
<?php
    class Arguments {
        public $help         = FALSE;
        public $input        = "php://stdin";
        public $output       = "php://stdout";
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
                    if (ctype_digit($tmp)/* and (int)$tmp >= 0*/) {
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

        public function check_arguments($argc) {
            if ($this->help == TRUE) {
                if ($argc != 2) {
                    err("Invalid use of program arguments", 1);
                }
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
                    "Created by Matejka Jiri (xmatej52)\n",
                    "-s                         values of type string will be transformed to text elements\n",
                    "-i                         numbers will be lements instead of atributes\n",
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
     * @param  int    $err return code
     */
    function err($str, $err) {
        fwrite(STDERR, $str . "\n");
        exit($err);
    }

    function add_types($value, XMLWriter $xml) {
        $str = gettype($value);
        if ($str === "boolean") {
            $str = "literal";
        }
        $xml->writeAttribute("type", $str);
    }

    function write_value($value, Arguments $args, XMLWriter $xml) {
        // TODO je validni?
        if (is_bool($value)) {
            if ($args->literal === TRUE) {
                if ($args->add_types === TRUE) {
                    add_types($value, $xml);
                }
                if ($value === TRUE) {
                    $xml->startElement("true");
                }
                else {
                    $xml->startElement("false");
                }
                $xml->endElement();
            }
            else {
                if ($value === TRUE) {
                    $xml->writeAttribute("value", "true");
                }
                else {
                    $xml->writeAttribute("value", "false");
                }
                if ($args->add_types === TRUE) {
                    add_types($value, $xml);
                }
            }
        }
        elseif (is_numeric($value)) {
            $new_value = floor($value);
            if ($args->itm2element === TRUE) {
                if ($args->add_types === TRUE) {
                    add_types($value, $xml);
                }
                $xml->writeRaw("$new_value");
            }
            else {
                $xml->writeAttribute("value", $value);
                if ($args->add_types === TRUE) {
                    add_types($value, $xml);
                }
            }
        }
        elseif (is_string($value)) {
            if ($args->str2element === TRUE) {
                if ($args->add_types === TRUE) {
                    add_types($value, $xml);
                }
                $xml->writeRaw($value);
            }
            else {
                $xml->writeAttribute("value", $value);
                if ($args->add_types === TRUE) {
                    add_types($value, $xml);
                }
            }
        }

        elseif ($value === NULL) {
            if ($args->literal === TRUE) {
                $xml->startElement("null");
                $xml->endElement();
            }
            else {
                $xml->writeAttribute("value", $value);
            }
        }
    }

    function proc_array($json, Arguments $args, XMLWriter $xml) {
        $xml->startElement($args->arr_name);
        if ($args->arr_size === TRUE) {
            $xml->writeAttribute("size",count($json));
        }
        $idx = $args->idx_start;
        foreach ($json as $key => $var) {
            $xml->startElement($args->item_name);
            if ($args->idx_item) {
                $xml->writeAttribute("index", $idx);
                $idx++;
            }
            write_value($var, $args, $xml);
            $xml->endElement();
        }

        $xml->endElement();
    }

    function recursive_write ($json, Arguments $args, XMLWriter $xml) {
//        echo "var_dump(is_array(\$json)): ";
//        var_dump(is_array($json)); // TODO co kdyz array nebude???
        if (is_array($json) === TRUE) {
            proc_array($json, $args, $xml);
        }
        else {
            foreach ($json as $key => $var) {
                if ($args->decode === TRUE) {
                    //TODO
                }
                //TODO zkontrolovat validitu elementu
                //var_dump($key);
                if (!is_integer($key)) {
                    $xml->startElement($key);
                    if (is_array($var) === TRUE) {
                        proc_array($var, $args, $xml);
                    }
                    elseif (is_object($var) === TRUE) {
                        recursive_write($var, $args, $xml);
                    }
                    else {
                        write_value($var, $args, $xml);
                    }
                    $xml->endElement();
                }
            }
        }
    }

    function read_input(Arguments $args) {
//        try {
            $input = file_get_contents($args->input);
//        } catch (Exception $e) {
            err("Can't open '$args->input' as input file.", 2);
//        }
        $json = json_decode($input, FALSE);
        if ($json === NULL) {
            err("Can't decode input data", 4);
        }
        return $json;
    }

    function write_output(Arguments $args, $json) {
        $xml = new XMLWriter();
        if ($xml->openMemory()  === FALSE) {
            err("XMLWriter error on openMemory method", 100); //TODO error code
        }
        $xml->setIndent(TRUE);

        if ($args->xml_header === TRUE) {
            $xml->startDocument('1.0','UTF-8');
        }
        if ($args->root_element != NULL) {
            $xml->startElement($args->root_element);
            recursive_write($json, $args, $xml);
            $xml->endElement();
        }
        else {
            recursive_write($json, $args, $xml);
        }
        $xml->endDocument();
        try {
            $output = fopen($args->output, "w");
        } catch (Exception $e) {
            err("Can't open '$args->output' as output file.", 3);
        }
        try {
            fwrite($output,$xml->outputMemory(TRUE));
        } catch (Exception $e) {
            err("Can't write to '$args->output' (output file)", 3);
        }
        if (fclose($output) == FALSE) {
            err("Can't close '$args->output' as output file.", 3);
        }
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
    $args->check_arguments($argc);
//    var_dump(get_object_vars($args));
    $json = read_input($args);
//    var_dump($json);
//    var_dump(is_array($json));
//    var_dump(is_object($json));
    write_output($args, $json);
?>
