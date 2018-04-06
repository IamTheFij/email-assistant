import DigitalDocument from './DigitalDocument';
import Invoice from './Invoice';
import BusReservation from './BusReservation';
import FlightReservation from './FlightReservation';
import TrainReservation from './TrainReservation';
import ParcelDelivery from './ParcelDelivery';

export default {
    BusReservation: {
        component: BusReservation,
        icon: 'directions_bus',
    },
    DigitalDocument: {
        component: DigitalDocument,
        icon: 'attach_file',
    },
    FlightReservation: {
        component: FlightReservation,
        icon: 'flight',
    },
    TrainReservation: {
        component: TrainReservation,
        icon: 'train',
    },
    Invoice: {
        component: Invoice,
        icon: 'receipt',
    },
    ParcelDelivery: {
        component: ParcelDelivery,
        icon: 'local_post_office',
    },
};
