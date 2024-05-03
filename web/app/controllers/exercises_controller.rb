class ExercisesController < ApplicationController
  before_action :set_exercises, only: [:index]
  before_action :set_collocations, only: [:new]

  # GET /exercises
  def index
    @feedback = {}
  end

  # POST /check-answer
  def check_answer
    exercise_id = params[:exercise_id]
    answer = params[:answer].strip.downcase

    # Load the specific exercise
    exercise = GrammarExercise.find(exercise_id)

    # Check the answer
    feedback = if answer == exercise.ready_verb.downcase
                 "Correct!"
               else
                 "Incorrect, try again!"
               end

    # Store feedback to show in the view
    @feedback = { exercise.id => feedback }
    set_exercises
    render :index
  end

  # GET /uploads/new
  def new
  end

  # POST /upload-pdf
  def upload_pdf
    uploaded_file = params[:file]

    # Handle file upload (e.g., save it to storage, parse it, etc.)
    if uploaded_file.content_type == 'application/pdf'
      # For example, save to file system or parse its content
      # Store the file as needed
      flash[:success] = "File uploaded successfully."
    else
      flash[:error] = "Invalid file type."
    end

    redirect_to new_upload_path
  end

  private

  def set_exercises
    # Example of loading exercises from database
    @exercises = GrammarExercise.all
  end

  def set_collocations
    # Example of loading collocations from database
    @collocations = Collocation.all
  end
end
