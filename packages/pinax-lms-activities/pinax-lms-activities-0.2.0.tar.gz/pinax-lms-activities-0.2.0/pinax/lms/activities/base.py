# coding: utf-8

from django.shortcuts import redirect, render

from django.contrib import messages

from .forms import SurveyForm


class Activity(object):

    def __init__(self, occurrence_state, activity_state):

        self.activity_state = activity_state
        self.occurrence_state = occurrence_state

        self.setup()

    def setup(self):
        pass


class Survey(Activity):

    def handle_request(self, request):

        if request.method == "POST":
            form = SurveyForm(request.POST, questions=self.questions)

            if form.is_valid():
                self.occurrence_state.data.update({"answers": form.cleaned_data})
                self.occurrence_state.mark_completed()
                if self.repeatable:
                    messages.success(request, "{} activity completed. You may repeat it again at any time.".format(self.title))
                else:
                    messages.success(request, "{} activity completed.".format(self.title))

                return redirect("dashboard")
        else:
            form = SurveyForm(questions=self.questions)

        return render(request, "activities/survey.html", {
            "title": self.title,
            "description": self.description,
            "help_text": getattr(self, "help_text", None),
            "form": form
        })


class MultiPageSurvey(Survey):

    def handle_request(self, request):

        data = self.occurrence_state.data

        if not data:
            data = {"page": 0}
        elif not data.get("page"):
            data["page"] = 0
        elif data["page"] == len(self.pages):
            messages.info(request, "{} activity already completed.".format(self.title))
            return redirect("dashboard")

        questions = self.pages[data["page"]]

        if request.method == "POST":
            form = SurveyForm(request.POST, questions=questions)

            if form.is_valid():
                self.occurrence_state.data.update({"answers_%d" % data["page"]: form.cleaned_data})
                self.occurrence_state.data.update({"page": data["page"] + 1})

                if data["page"] == len(self.pages):
                    self.occurrence_state.mark_completed()
                    if self.repeatable:
                        messages.success(request, "{} activity completed. You may repeat it again at any time.".format(self.title))
                    else:
                        messages.success(request, "{} activity completed.".format(self.title))

                    return redirect("dashboard")
                else:
                    self.occurrence_state.save()

                    return redirect("activity_play", self.occurrence_state.activity_slug)
        else:
            form = SurveyForm(questions=questions)

        return render(request, "activities/survey.html", {
            "title": self.title,
            "description": self.description,
            "help_text": getattr(self, "help_text", None),
            "page_number": data["page"] + 1,
            "num_pages": len(self.pages),
            "form": form
        })


class Quiz(Activity):

    extra_context = {}

    def setup(self):
        if not self.occurrence_state.data:
            self.occurrence_state.data = {"questions": self.construct_quiz()}
            self.occurrence_state.save()
        elif not self.occurrence_state.data.get("questions"):
            self.occurrence_state.data["questions"] = self.construct_quiz()
            self.occurrence_state.save()

    def get_data(self):
        data = self.occurrence_state.data
        if not data:
            data = {"question_number": 0}
        elif not data.get("question_number"):
            data["question_number"] = 0
        elif data["question_number"] == len(data["questions"]):
            data = None
        return data

    def handle_request(self, request):

        data = self.get_data()
        if data is None:
            messages.info(request, "{} activity already completed.".format(self.title))
            return redirect("dashboard")

        question = data["questions"][data["question_number"]]

        if request.method == "POST":
            if request.POST.get("question_number") == str(data["question_number"] + 1):
                answer = request.POST.get("answer")

                if answer in self.valid_answer:
                    self.occurrence_state.data.update({"answer_%d" % data["question_number"]: answer})
                    self.occurrence_state.data.update({"question_number": data["question_number"] + 1})

                    if data["question_number"] == len(data["questions"]):
                        self.occurrence_state.mark_completed()
                        if self.repeatable:
                            messages.success(request, "{} activity completed. You may repeat it again at any time.".format(self.title))
                        else:
                            messages.success(request, "{} activity completed.".format(self.title))

                        return redirect("dashboard")
                    else:
                        self.occurrence_state.save()

                        return redirect("activity_play", self.occurrence_state.activity_slug)

        ctx = {
            "title": self.title,
            "description": self.description,
            "help_text": getattr(self, "help_text", None),
            "question_number": data["question_number"] + 1,
            "num_questions": len(data["questions"]),
            "question": question,
        }
        ctx.update(self.extra_context)

        return render(request, self.template_name, ctx)


class TwoChoiceQuiz(Quiz):

    template_name = "activities/two_choice_quiz.html"
    valid_answer = ["left", "right"]


class LikertQuiz(Quiz):

    template_name = "activities/likert_quiz.html"
    valid_answer = ["1", "2", "3", "4", "5"]

    @property
    def extra_context(self):
        return {"scale": self.scale}


class QuizWithAnswers(Quiz):

    def previous_question_ansewr(self, data):
        previous_question = None
        previous_answer = None
        if data["question_number"] > 0:
            previous_question = data["questions"][data["question_number"] - 1]
            previous_answer = data["answer_%d" % (data["question_number"] - 1)]
            if previous_answer in ["left", "L2", "L1"]:
                previous_answer = previous_question[1][0]
            elif previous_answer in ["right", "R2", "R1"]:
                previous_answer = previous_question[1][1]
            elif previous_answer == "0":
                previous_answer = "you didn't know"
        return previous_question, previous_answer

    def handle_request(self, request):
        data = self.get_data()
        if data is None:
            messages.info(request, "{} activity already completed.".format(self.title))
            return redirect("dashboard")

        question = data["questions"][data["question_number"]]

        previous_question, previous_answer = self.previous_question_ansewr(data)

        if request.method == "POST":
            if request.POST.get("question_number") == str(data["question_number"] + 1):
                answer = request.POST.get("answer")

                if answer in self.valid_answer:
                    self.occurrence_state.data.update({"answer_%d" % data["question_number"]: answer})
                    self.occurrence_state.data.update({"question_number": data["question_number"] + 1})

                    if data["question_number"] == len(data["questions"]):
                        self.occurrence_state.mark_completed()

                        return redirect("activity_completed", self.occurrence_state.activity_slug)
                    else:
                        self.occurrence_state.save()

                        return redirect("activity_play", self.occurrence_state.activity_slug)

        ctx = {
            "title": self.title,
            "description": self.description,
            "help_text": getattr(self, "help_text", None),
            "question_number": data["question_number"] + 1,
            "num_questions": len(data["questions"]),
            "question": question,
            "previous_question": previous_question,
            "previous_answer": previous_answer,
            "question_template": self.question_template,
            "answer_template": self.answer_template,
        }
        ctx.update(self.extra_context)

        return render(request, self.template_name, ctx)

    def completed(self, request):

        data = self.occurrence_state.data

        results = []

        for i, question in enumerate(data["questions"]):
            answer = data["answer_%d" % i]
            if answer in ["left", "L2", "L1"]:
                answer = question[1][0]
            elif answer in ["right", "R2", "R1"]:
                answer = question[1][1]
            elif answer == "0":
                answer = None
            results.append((question, answer))

        ctx = {
            "title": self.title,
            "description": self.description,
            "help_text": getattr(self, "help_text", None),
            "results": results,
            "slug": self.activity_state.activity_slug,
            "answer_template": self.answer_template,
        }
        ctx.update(self.extra_context)

        return render(request, self.completed_template_name, ctx)


class TwoChoiceWithAnswersQuiz(QuizWithAnswers):

    template_name = "activities/two_choice_with_answers_quiz.html"
    completed_template_name = "activities/two_choice_with_answers_quiz_completed.html"
    question_template = "activities/_question.html"
    answer_template = "activities/_answer.html"
    valid_answer = ["left", "right"]


class TwoChoiceLikertWithAnswersQuiz(QuizWithAnswers):

    template_name = "activities/two_choice_likert_with_answers_quiz.html"
    completed_template_name = "activities/two_choice_with_answers_quiz_completed.html"
    question_template = "activities/_question.html"
    valid_answer = ["L2", "L1", "0", "R1", "R2"]
