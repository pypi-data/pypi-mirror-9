# How to Contribute
1. Read and complete the [Contributor License Agreement](https://github.com/tagged/netscaler-tool/blob/master/CLA.txt).
1. When complete, email a PDF of the signed agreement to [legal@tagged.com](mailto:legal@tagged.com).
1. Once you have received a confirmation that your signed CLA was received, contribute your code, documentation, or any other materials with a pull request.

## Coding Style
* PEP8
* Indents are 4 whitespaces

### Add a new top level argument, i.e. show
1. Creating a new parser off of the main subparser
   
   ```parser_show = subparser.add_parser(
      'show', help='sub-command for showing objects'
   )```


### Add a new second level argument, i.e. lb-vservers
1. Create a new subparser off of parent subparser
    * `subparser_show = parser_show.add_subparsers(dest='subparser_name')`
1. Create parser

        subparser_show.add_parser('lb-vservers', help='Shows all lb vservers')

    * If the subparser will need an argument
        -
        ```parser_show_lbvserver.add_argument(
            'vserver', help='Shows stats for specified vserver'
        )```

1. Create new method under respective class

        def lbvservers(self):
            ns_object = ["lbvserver"]
            list_of_lbvservers = []

            try:
                output = self.client.get_object(ns_object)
            except RuntimeError as e:
                msg = "Problem while trying to get list of LB vservers " \
                      "on %s.\n%s" % (self.args.host, e)
                raise RuntimeError(msg)

            for vserver in output['lbvserver']:
                list_of_lbvservers.append(vserver['name'])

            utils.print_list(sorted(list_of_lbvservers))
