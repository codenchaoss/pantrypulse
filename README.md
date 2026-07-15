# pantrypulse
A restaurant back-of-house application that monitors wholesale ingredient storage and suggests 
daily menu updates. 
● Frontend (React): A kitchen tablet view showcasing current inventory, shelf-life 
warnings, and recipe suggestions. 
● Backend (Spring Boot): Controls ingredient inventories, point-of-sale data integrations, 
and vendor orders. 
● AWS Services: Amazon DynamoDB (stores perishable item metrics) and Amazon RDS 
(relational recipe and sales history logs). 
● Generative AI Stack: LangChain4j links remaining product weights with popular recipe 
books, Nous Hermes builds high-margin special menu suggestions, and OpenClaw 
handles supplier messaging. 
The End-to-End Workflow 
1. A kitchen stock manager registers an excess inventory of fresh salmon nearing its shelf 
life in DynamoDB. 
2. Spring Boot alerts the system, prompting LangChain4j to cross-reference historical guest 
order records in RDS. 
3. Nous Hermes creates an appealing, high-margin evening seafood special recipe 
designed to use up the remaining stock. 
4. OpenClaw sends the completed recipe to the front-of-house printing queue and updates 
the digital menu displays.
