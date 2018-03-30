import BusReservation from './BusReservation';
import FlightReservation from './FlightReservation';
import ParcelDelivery from './ParcelDelivery';

export default {
    BusReservation: {
        component: BusReservation,
        icon: 'directions_bus',
    },
    FlightReservation: {
        component: FlightReservation,
        icon: 'flight',
    },
    ParcelDelivery: {
        component: ParcelDelivery,
        icon: 'local_post_office',
    },
};
