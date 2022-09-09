import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

db = SQLAlchemy()

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    setup_db(app)

    #Set up CORS with "*" for origins. Delete the sample route after completing the TODOs
    CORS(app, resources={"/" : {"origins": "*"}})

    #Use the after_request decorator to set Access-Control-Allow
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type, Authorization"
        )
        response.headers.add(
            "Access-Control-Allow-Headers", "GET, POST, PATCH, DELETE, OPTION"
        )
        return response


    @app.route("/categories")
    def get_categories():
        # Create an endpoint to handle GET requestsfor all available categories.
        categories= Category.query.order_by(Category.type).all()

        if len(categories) == 0:
            abort(404)

        return jsonify({
            "success": True,
            "categories": {category.id: category.type for category in categories}
        })


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route("/questions")
    # @cross_origin
    def get_questions():
        # Implement pagination
        page = request.args.get("page", 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = Question.query.all()
        formatted_questions = [question.format() for question in questions]
        categories= Category.query.order_by(Category.type).all()

        if len(formatted_questions) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": formatted_questions[start:end],
                "total_questions": len(formatted_questions),
                "categories": {category.id: category.type for category in categories},
                "current_category": None,
            }
        )

    """
    TEST: When you click the trash icon next to a question, the question will be removed
    & persists in the database and when you refresh the page.
    """
    #endpoint to DELETE question using a question ID.

    @app.route("/questions/<question_id>", methods=["DELETE"])
    def delete_question(id):
        try:
            question = Question.query.get(id)
            question.delete()

            return jsonify({
                "success": True,
                "deleted": id
            })

        except:
            abort(422)
    """
    @TODO:
    It will require the question and answer text,
    category, and difficulty score.
    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    #endpoint to POST a new question
    @app.route("/questions", methods=["POST"])
    def add_question():
        body = request.get_json()

        if not ("question" in body and "answer" in body and "difficulty" in body and "category" in body):
            abort(422)

        new_question = body.get("question")
        new_answer = body.get("answer")
        new_difficulty = body.get("difficulty")
        new_category = body.get("category")

        try:
            question = Question(question= new_question, answer= new_answer, difficulty= new_difficulty,  category= new_category)
            question.insert()

            questions = Question.query.all()
            formatted_questions = [question.format() for question in questions]

            return jsonify({
                "success": True,
                "created": question.id,
                "total_questions": len(formatted_questions),
            })

        except:
            abort(422)

    """
    @TODO:
    Search should return any questions for whom the search term
    is a substring of the question.

    Try using the word "title" to start search.
    """


    #endpoint to get questions based on a search term
    @app.route("/questions/search", methods=["POST"])
    def search_question():
        body = request.get_json()
        searched_term = body.get("searchTerm", None)

        #Search by any phrase & questions list will update
        #to include only questions that include that string within them.
        if searched_term:
            search_results = Question.query.filter(
                Question.question.ilike(f"%{searched_term}%")).all()

            return jsonify({
                "success": True,
                "questions": [question.format() for question in search_results],
                "total_questions": len(search_results),
                "current_category": None
            })
        abort(404)

    """
    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    #endpoint to get questions based on category.
    @app.route("/categories/<int:id>/questions", methods=["GET"])
    def get_questions_by_category(id):

        try:
            questions = Question.query.filter(
                Question.category == str(id)).all()

            return jsonify({
                "success": True,
                "questions": [question.format() for question in questions],
                "total_questions": len(questions),
                "current_category": id
            })

        except:
            abort(404)
    """
    @TODO:
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    #POST endpoint to get questions to play the quiz.
    @app.route("/quizzes", methods=["POST"])
    def play_quiz():

        try:
            body = request.get_json()

            category = body.get("quiz_category")
            previous_questions = body.get("previous_questions")

            if not ("quiz_category" in body and "previous_questions" in body):
                abort(422)


            if category["type"] == "click":
                #filter all available questns
                questions_available = Question.query.filter(
                    Question.id.notin_((previous_questions))).all()
            else:
                #filter available questns by category also
                questions_available = Question.query.filter_by(
                    category=category["id"]).filter(Question.id.notin_((previous_questions))).all()

            new_question = questions_available[random.randrange(
                0, len(questions_available))].format() if len(questions_available) > 0 else None

            return jsonify({
                "success": True,
                "question": new_question
            })
        except:
            abort(400)


    #Error handlers for all expected errors (including 404 and 422).
    #HTTP status codes and message
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    return app

