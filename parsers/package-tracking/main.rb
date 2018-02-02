require 'sinatra'
require 'tracking_number'

set :bind, "0.0.0.0"
set :port, 3000

# Simple status endpoint on root
get '/' do
    'OK'
end

# Standard parser api receives PUT {"message": "Email body"} /parse
# Returns [{"token": "extracted token", "type": "token type", "metadata": {}]
post '/parse' do
    body = JSON.parse(request.body.read)
    trackers = TrackingNumber.search(body["message"])
    results = []
    for tracker in trackers do
        results.push({
            :token => tracker.tracking_number,
            :type => "SHIPPING",
            :metadata => {}
        })
    end
    JSON.dump(results)
end
