# Library Management System
Backend project to create a student directory for libraries.



## Tech Stack
* FastAPI
* MongoDB
## Demo
[Click here](https://library-management-system-qtn2.onrender.com/docs#/) for live demo.


## Run Locally

Clone the project

```bash
  git clone https://link-to-project
```

Go to the project directory

```bash
  cd my-project
```

Install dependencies

```bash
  pip install pipenv
  pipenv shell  
  pipenv install requirements.txt
```

Start the server

```bash
  uvicorn main:app --reload
```
To run this project, you will need to add `DATABASE_URL` to your .env file



## API Reference

#### Create a student entry

```http
  POST /students
```



#### Get all students

```http
  GET /students
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `Country` | `string` | **Optional**. Filter to get students of a givem country |
| `Age` | `Integer` | **Optional**. Filter to get students greater than or equal to given age |

#### Get student

```http
  GET /students/{id}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `id`      | `string` | **Required**. Id of student to fetch |

#### Update student entry

```http
  PATCH /students/{id}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `id`      | `string` | **Required**. Id of student to fetch |

#### Delete student

```http
  DELETE /students/{id}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `id`      | `string` | **Required**. Id of student to fetch |



## Author

[AdvaitP10](https://www.github.com/AdvaitP10)

