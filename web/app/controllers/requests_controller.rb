require 'net/http'
require 'uri'
require 'json'

class RequestsController < ApplicationController
  def new

  end

  def show
    request = request_params[:request]
    uri = URI('http://' + ENV['REST_SERVER_IP'])
    uri.port = 5005
    uri.path = '/model'
    req = Net::HTTP::Post.new(uri)
    req.body = { "x": [ request ] }.to_json
    req.content_type = 'application/json'

    res = Net::HTTP.start(uri.hostname, uri.port) do |http|
      http.request(req)
    end

    @last_request = request_params[:request]
    @doc_names = ResponseConverter.get_doc_names_sorted(res.body)

    render :new
  end

  private

  def request_params
    params.permit(:request, :commit)
  end

end
