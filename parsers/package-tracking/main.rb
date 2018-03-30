require 'sinatra'
require 'tracking_number'

set :bind, ENV['HOST'].present? ? ENV['HOST'] : "0.0.0.0"
set :port, ENV['PORT'].present? ? ENV['PORT'] : 3000


def get_tracking_url(tracker)
    tracking_urls = {
        :ups => 'https://wwwapps.ups.com/WebTracking/track?track=yes&trackNums=%s',
        :dhl => 'http://www.dhl.com/en/express/tracking.html?brand=DHL&AWB=%s',
        :fedex => 'https://www.fedex.com/apps/fedextrack/?tracknumbers=%s',
        :ontrac => 'http://www.ontrac.com/trackingres.asp?tracking_number=%s',
        :usps => 'https://m.usps.com/m/TrackConfirmAction_detail?tLabels=%s',
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
    message = body['message']['plain'] ? body['message']['plain'] : body['message']['html']
    trackers = TrackingNumber.search(message)
    results = []
    for tracker in trackers do
        if not body['from'].include? tracker.courier_name
            next
        end
        results.push({
            :token => tracker.tracking_number,
            :type => 'ParcelDelivery',
            :metadata => {
                :provider => {
                    :@type => 'provider',
                    :@context => 'http://schema.org',
                    :name => tracker.courier_name,
                },
                :trackingUrl => get_tracking_url(tracker),
                :trackingNumber => tracker.tracking_number,
            }
        })
    end
    JSON.dump(results)
end
