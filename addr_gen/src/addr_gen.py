"""
The code below is written by Wojciech M. Zabolotny ( wzab01<at>gmail.com or wzab<at>ise.pw.edu.pl)
9-11.02.2018 and is published as Public domain or under Creative Commons CC0 license.
It is used to generate the map of addresses for VHDL designs using the vector of control
or status registers to communicate with software (via IPbus, AXI-Lite or other bus.)
"""
import sys
class const:
  pass

class glob:
  pass

# Class "addressable object"
class aobj(object):
  def __init__(self,name,children=[]):
     global glb
     self.children=children
     self.name=name
     glb.defs.append(self)
  def a(self,child):
     self.children.append(child)
  def gen_vhdl_types(self):
     # This function browses the definition and generates the necessary types
     if (self.name=="SREG") or (self.name == "CREG"):
        res = "subtype TAD_"+self.name+" is integer;\n"
        res += "type TAD_ARR_"+self.name+" is array(natural range <>) of integer;\n"
     else:
        res = "type TAD_"+self.name+" is record\n"
        for cd in self.children:
           if len(cd)==2:
              #single object
              res+="  "+cd[0]+" : TAD_"+cd[1].name+";\n"
           elif len(cd)==3:
              #array of objects
              res+="  "+cd[0]+" : TAD_ARR_"+cd[1].name+"(0 to "+str(cd[2]-1)+");\n"
        res += "end record TAD_"+self.name+";\n"
        res += "type TAD_ARR_"+self.name+" is array(natural range <>) of TAD_"+self.name+";\n"
     return res
  def gen_vhdl_addr(self,creg_base,sreg_base):
     #This function returns the initializer with addresses, creg_base is the base for control registers
     #sreg_base is the base for status registers
     res=""
     if self.name=="SREG":
        res += str(sreg_base)
        sreg_base+=1
     elif self.name=="CREG":
        res += str(creg_base)
        creg_base+=1
     else:
        first_child=True,
        if len(self.children)>0:
          res+="("
        for cd in self.children:
          if first_child:
             first_child=False
          else:
             res+=","
          if len(cd)==2:
             #single object
             (nres,creg_base,sreg_base)=cd[1].gen_vhdl_addr(creg_base,sreg_base)
             res+=nres
          elif len(cd)==3:
             #array of objects
             res+="("
             for i in range(0,cd[2]):
                 (nres,creg_base,sreg_base)=cd[1].gen_vhdl_addr(creg_base,sreg_base)
                 res+=nres
                 if i<(cd[2]-1):
                   res+=", "
             res+=")"
        if len(self.children)>0:
          res+=")"
     return (res,creg_base,sreg_base)

  def gen_python_addr(self,creg_base,sreg_base):
     #This function returns the Python code with addresses in a dictionary
     #creg_base is the base for control registers
     #sreg_base is the base for status registers
     res=""
     if self.name=="SREG":
        res += str(sreg_base)
        sreg_base+=1
     elif self.name=="CREG":
        res += str(creg_base)
        creg_base+=1
     else:
        first_child=True,
        if len(self.children)>0:
          res+="{"
        for cd in self.children:
          if first_child:
             first_child=False
          else:
             res+=","
          if len(cd)==2:
             #single object
             (nres,creg_base,sreg_base)=cd[1].gen_python_addr(creg_base,sreg_base)
             res+="'"+cd[0] +"' : "+nres
          elif len(cd)==3:
             #array of objects
             res+="'"+cd[0]+"' :("
             for i in range(0,cd[2]):
                 (nres,creg_base,sreg_base)=cd[1].gen_python_addr(creg_base,sreg_base)
                 res+=nres
                 if i<(cd[2]-1):
                   res+=", "
             res+=")"
        if len(self.children)>0:
          res+="}"
     return (res,creg_base,sreg_base)

  def gen_ipbus_xml(self,node_name,indent,creg_base,sreg_base):
     res=""
     if self.name=="SREG":
        res +=indent*" "+"<node id=\""+node_name+"\" address=\""+hex(sreg_base)+"\" mode=\"r\"/>\n"
        sreg_base+=1
     elif self.name=="CREG":
        res +=indent*" "+"<node id=\""+node_name+"\" address=\""+hex(creg_base)+"\" mode=\"rw\"/>\n"
        creg_base+=1
     else:
        res += indent*" "+"<node id=\""+node_name+"\">\n"
        for cd in self.children:
          if len(cd)==2:
             #single object
             (nres,creg_base,sreg_base)=cd[1].gen_ipbus_xml(cd[0],indent+2,creg_base,sreg_base)
             res+=nres
          elif len(cd)==3:
             #array of objects
             for i in range(0,cd[2]):
                 (nres,creg_base,sreg_base)=cd[1].gen_ipbus_xml(cd[0]+"["+str(i)+"]",indent+2,creg_base,sreg_base)
                 res+=nres
        res += indent*" "+"</node>\n"
        first_child=True,
     return (res,creg_base,sreg_base)

def gen_types():
  global glb
  res=""
  for x in glb.defs:
     res+=x.gen_vhdl_types()
  #print(res)
  return res

def gen_vhdl_const_package(pkg_name,file_name=""):
  if file_name=="":
    file_name=pkg_name+".vhd"
  fo = open(file_name,"w")
  fo.write("\n")
  fo.write("-- This file is automatically generated by the "+sys.argv[0]+" script\n")
  fo.write("-- All modifications should be done in that file\n--\n")
  fo.write("library ieee;\nuse ieee.std_logic_1164.all;\n")
  fo.write("use ieee.numeric_std.all;\n\n")
  fo.write("package "+pkg_name+" is\n\n")
  global c
  for k, v in vars(c).items():
    fo.write("  constant "+k+" : integer := "+str(v)+";\n")
  fo.write("\nend package "+pkg_name+";\n")
  fo.close()

def gen_vhdl_addr_package(pkg_name,file_name,root,creg_base,sreg_base):
  if file_name=="":
    file_name=pkg_name+".vhd"
  fo = open(file_name,"w")
  fo.write("-- This file is automatically generated by the "+sys.argv[0]+" script\n")
  fo.write("-- All modifications should be done in that file\n--\n")
  fo.write("library ieee;\nuse ieee.std_logic_1164.all;\n")
  fo.write("use ieee.numeric_std.all;\n\n")
  fo.write("package "+pkg_name+" is\n\n")
  #generate types
  res=gen_types()
  fo.write(res)
  (res,creg_base,sreg_base)=root.gen_vhdl_addr(creg_base,sreg_base)
  fo.write("constant tad_addr : TAD_"+root.name+" := "+res+";\n\n")
  fo.write("constant TAD_CREG_NUM : natural := " + str(creg_base) + ";\n")
  fo.write("constant TAD_SREG_NUM : natural := " + str(sreg_base) + ";\n")
  fo.write("\nend package "+pkg_name+";\n")
  fo.close()

def gen_python_addr_module(module_name,root,creg_base,sreg_base):
  """The function creates the dictionary, and then converts it to an object accessible via attributes"""
  fo = open(module_name+".py","w")
  fo.write(""
    "\"\"\"This file is automatically generated by the "+sys.argv[0]+" script\n"
    "All modifications should be done in that file\n\"\"\"\n"+
    root.name+"_dict=")
  (res,creg_base,sreg_base)=root.gen_python_addr(creg_base,sreg_base)
  fo.write(res+"\n")
  fo.write(""
  "#Convert the dictionary to object, as described in https://stackoverflow.com/a/6993694/1735409\n"
  "class Struct(object):\n"
  "  def __init__(self, data):\n"
  "      for name, value in data.items():\n"
  "          setattr(self, name, self._wrap(value))\n"
  "  def _wrap(self, value):\n"
  "      if isinstance(value, (tuple, list, set, frozenset)):\n"
  "          return type(value)([self._wrap(v) for v in value])\n"
  "      else:\n"
  "          return Struct(value) if isinstance(value, dict) else value\n"+
  root.name+"=Struct("+root.name+"_dict)\n")
  fo.close()

def gen_ipbus_xml_table(module_name,root,creg_base,sreg_base):
  fo = open(module_name+".xml","w")
  #fo.write(""
  #"")
  (res,creg_base,sreg_base)=root.gen_ipbus_xml(module_name,0,creg_base,sreg_base)
  fo.write(res)
  fo.close()

glb = glob()
glb.defs=[]
sreg_def=aobj("SREG")
creg_def=aobj("CREG")
c=const()


