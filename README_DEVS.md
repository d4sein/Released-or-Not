### Format for pull requests

1. Documentation  
    The code should have decent documentation, using PEP8 as a guide is a great idea.  
    Docstrings for functions and methods outside the Application class must follow this structure:  
    ```python
    async def function(a: str, b: bool=False, c: str=None) -> None:
        '''What the function does
        
        Parameters:
            a: str
            Description of the `a` parameter
            
            b: bool
            Description of the `b` parameter
            Optional -> Defaults to: False
            
            c: str
            Description of the `c` parameter
            Optional -> Defaults to: None
        '''
    ```

2. Asynchronous  
    The functions and methods must be asynchronous (except Exceptions).
