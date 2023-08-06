import json
class JSON_Parser():
    def __init__(self):
        self.index = 1

    def parse_textfile(self, textfile):
        lines = textfile.split('\r\n')
        json_output = {}
        for line in lines:
            if line:
                parsed_line = self.parse_line(line)
                json_output = JSON_Parser.add_line(json_output, parsed_line)
        json_output = JSON_Parser.remove_orphan_blocks(json_output)
        return json.dumps(json_output, sort_keys=True,indent=2, separators=(',', ': '))

    def parse_line(self, line):
        [tags, value] = line.split(':')
        words = tags.split(' ')
        parent_tag = words[0]
        child_tag = ''.join(words[1:])
        if child_tag == 'Status':
            child_tag = child_tag + str(self.index)
            self.index += 1

        return {parent_tag : {child_tag : value}}

    @classmethod
    def add_line(cls, json_info, line):
        parent_tag = line.keys()[0]
        child_tag = line[parent_tag].keys()[0]
        if json_info.has_key(parent_tag):
            jp_type = type(json_info[parent_tag])
            if jp_type == dict:
                if json_info[parent_tag].has_key(child_tag):
                    old_value = json_info[parent_tag]
                    json_info[parent_tag]=[old_value]
                    json_info[parent_tag].append(line[parent_tag])
                else:
                    json_info[parent_tag].update(line[parent_tag])
            elif jp_type == list:
                if json_info[parent_tag][-1].has_key(child_tag):
                    json_info[parent_tag].append(line[parent_tag])
                else:
                    json_info[parent_tag][-1].update(line[parent_tag])
            else:
                raise Exception('Unknown jp_type')
        else:
            json_info.update(line)
        # print 'NEW ITERATION'
        # print json.dumps(json_info, indent=2, separators=(',',': '))
        return json_info

    @classmethod
    def remove_orphan_blocks(cls,json_out):
        out=[]
        for item in json_out['Loan']:
            if item.has_key('AwardID'):
                out.append(item)
        json_out['Loan']=out
        return json_out

