import BusReservation from './BusReservation';
import DigitalDocument from './DigitalDocument';
import FlightReservation from './FlightReservation';
import Invoice from './Invoice';
import ParcelDelivery from './ParcelDelivery';
import ProgramMembership from './ProgramMembership';
import TrainReservation from './TrainReservation';

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
    ProgramMembership: {
        component: ProgramMembership,
        icon: 'account_balance_wallet',
    },
};
