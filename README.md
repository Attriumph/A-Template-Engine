# A-Template-Engine
A tool suited to solve text-heavy problems with relatively less logic in program development. 
  
  Author:Ned Batchelder
  
  Refer: [MichaelDiBernardo's GitHub](https://github.com/aosabook/500lines/tree/master/template-engine " ")
    

## Introducation:
  Web Application creates HTML files and send it to browser.A big progbem developer facing is that how best to generate a large string       containing a mix of static and dynamic data?

> (1)One way: Have string constants in code, and join them together to produce the page. Dynamic data would be inserted with string   
substitution of some sort.  
>> Disadvantages: The logic of the page is hard to see because the static text is broken into separate pieces.The details of how data is formatted is lost in the Python code.
       
   In order to modify the HTML page, our front-end designer would need to be able to edit Python code to make HTML changes.

> (2)A better way to produce HTML pages is with templates.  
>> Advantages: 
>>>  - more logics are represented in static text.  
>>> - "模板语言恰好相反：它大多是静态文字文本，同时用特殊的符号表示可执行的动态部分。"
  
  *These files are called templates because they are used to produce many pages with similar structure but differing details.
  *The engine is comprise of a function that takes a static template describing the structure and static content of the page, and a   
     dynamic context that provides the dynamic data to plug into the template. 

> There are two methods to render a template.
>> 1. compile: parsing produce the exctuable code.  
>> 2. inteprete: we choose this method


For implementing engine，our goal is to compile the template to Python.

