# app/controllers/collocations_controller.rb
class CollocationsController < ApplicationController
  def display
    @collocations_data = JSON.parse(params[:data])
  end
end
