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
        public $decote       = FALSE;
        public $arr_size     = FALSE;
        public $idx_item     = FALSE;
        public $idx_start    = 1;
        public $add_types    = FALSE;

        /**
         * Constructor of class Arguments
         * @param [type] $arg arguments of program
         */
        public function __construct($arguments) {
            foreach ($arguments as $arg) {
                if ($arg == "--help") {
                    $this->help = TRUE;
                }
                elseif ($arg == "-s") {
                    $this->str2element = TRUE;
                }
                elseif ($arg == "-i") {
                    $this->itm2element = TRUE;
                }
                elseif ($arg == "-v") {
                    $this->literal = TRUE;
                }
                elseif ($arg == "-c") {
                    $this->decote = TRUE;
                }
                elseif ($arg == "-n") {
                    $this->xml_header = FALSE;
                }
                elseif ($arg == "-a" or $arg == "--array-size") {
                    $this->arr_size = TRUE;
                }
                elseif ($arg == "-t" or $arg == "--index-items") {
                    $this->idx_item = TRUE;
                }
                elseif ($arg == "--types") {
                    $this->add_types = TRUE;
                }
            }
        }

        /**
         * Print manual page on standart output and exit program with return code 0
         */
        private function print_help() {
            echo    "Usage: php ./proj1 --input=filename --output=filename",
                    "[-s -i -c -n --help -h=subst -r=root-element -a -t --start --types --array-name=array-element --item-name=item-element]\n",
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
     * @param  [type] $str error message
     * @param  [type] $err return code
     */
    function err($str, $err) {
        fwrite(STDERR, $str);
        exit($err);
    }

    unset($argv[0]);
    $my_var = new Arguments($argv);
    print_r(get_object_vars($my_var))
?>
