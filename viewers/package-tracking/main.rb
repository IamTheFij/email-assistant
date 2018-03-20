require 'sinatra'
require 'trackerific'

set :bind, ENV['HOST'].present? ? ENV['HOST'] : "0.0.0.0"
set :port, ENV['PORT'].present? ? ENV['PORT'] : 3000

Trackerific.configure do |config|
    if [
            ENV['FEDEX_KEY'].present?,
            ENV['FEDEX_PASSWORD'].present?,
            ENV['FEDEX_ACCOUNT_NUMBER'].present?,
            ENV['FEDEX_METER_NUMBER'].present?,
    ].all?
        config.fedex = {
            key: ENV['FEDEX_KEY'],
            password: ENV['FEDEX_PASSWORD'],
            account_number: ENV['FEDEX_ACCOUNT_NUMBER'],
            meter_number: ENV['FEDEX_METER_NUMBER'],
        }
    end

    if [
            ENV['UPS_KEY'].present?,
            ENV['UPS_USER_ID'].present?,
            ENV['UPS_PASSWORD'].present?,
    ].all?
        config.ups = {
            key: ENV['UPS_KEY'],
            user_id: ENV['UPS_USER_ID'],
            password: ENV['UPS_PASSWORD'],
        }
    end
    if [
            ENV['USPS_USER_ID'].present?,
    ].all?
        config.usps = {
            user_id: ENV['USPS_USER_ID'],
        }
    end
end

# Simple status endpoint on root
get '/' do
    'OK'
end

get '/info/:token' do |token|
    details = Trackerific.track(token)
    details[0].to_json()
end
