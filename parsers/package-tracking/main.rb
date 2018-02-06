require 'sinatra'
require 'tracking_number'

set :bind, '0.0.0.0'
set :port, 3000


def get_tracking_url(tracker)
    tracking_urls = {
        :ups => 'https://wwwapps.ups.com/WebTracking/track?track=yes&trackNums=%s',
    }
    tracking_url = tracking_urls[tracker.courier_code]
    if tracking_url != nil
        tracking_url = tracking_url % tracker.tracking_number
    end
    return tracking_url
end

# Simple status endpoint on root
get '/' do
    'OK'
end

# Standard parser api receives PUT {"message": "Email body"} /parse
# Returns [{"token": "extracted token", "type": "token type", "metadata": {}]
post '/parse' do
    body = JSON.parse(request.body.read)
    trackers = TrackingNumber.search(body['message'])
    results = []
    for tracker in trackers do
        results.push({
            :token => tracker.tracking_number,
            :type => 'SHIPPING',
            :metadata => {
                :carrier_name => tracker.courier_name,
                :tracking_url => get_tracking_url(tracker),
            }
        })
    end
    JSON.dump(results)
end
