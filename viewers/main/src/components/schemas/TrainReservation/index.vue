<template>
    <v-data-table
        :headers="headers"
        :items="tableItems">
        <template slot="items" slot-scope="props">
            <td>{{ props.item.id }}</td>
            <td>{{ props.item.name }}</td>
            <td>{{ props.item.reservationNumber }}</td>
            <td>{{ props.item.trainNumber }}</td>
            <td>{{ props.item.from }}</td>
            <td>{{ props.item.to }}</td>
            <td><Barcode :value="props.item.boardingPass" v-if="props.item.boardingPass"></Barcode></td>
            <td>{{ props.item.seat }}</td>
            <td>{{ props.item.status }}</td>
        </template>
    </v-data-table>
</template>

<script>
import moment from 'moment';

import Barcode from '@/components/Barcode';

export default {
    components: {
        Barcode,
    },
    computed: {
        tableItems() {
            return this.items.map(this.formatTrainReservationItem);
        },
    },
    data() {
        return {
            headers: [
                {
                    text: '#',
                    value: 'id',
                },
                {
                    text: 'Name',
                    value: 'name',
                },
                {
                    text: 'Reservation number',
                    value: 'reservationNumber',
                },
                {
                    text: 'Train number',
                    value: 'trainNumber',
                },
                {
                    text: 'From',
                    value: 'from',
                },
                {
                    text: 'To',
                    value: 'to',
                },
                {
                    text: 'Boarding pass',
                    value: 'boardingPass',
                },
                {
                    text: 'Seat',
                    value: 'seat',
                },
                {
                    text: 'Status',
                    value: 'status',
                },
            ],
        };
    },
    methods: {
        formatTrainReservationItem(item) {
            let from = '';
            try {
                const fromStopName = item.metadata.reservationFor.departureStation.name;
                const fromDateTime = moment(
                    item.metadata.reservationFor.departureTime,
                ).local().format('HH:mm DD/MM/YYYY');
                from = `${fromStopName} @ ${fromDateTime}`;
            } catch (e) {}  // eslint-disable-line no-empty

            let to = '';
            try {
                const toStopName = item.metadata.reservationFor.arrivalStation.name;
                const toDateTime = moment(
                    item.metadata.reservationFor.arrivalTime,
                ).local().format('HH:mm DD/MM/YYYY');
                to = `${toStopName} @ ${toDateTime}`;
            } catch (e) {}  // eslint-disable-line no-empty

            let seat = '';
            try {
                seat = `Coach ${item.metadata.reservedTicket.ticketedSeat.seatSection}, seat ${item.metadata.reservedTicket.ticketedSeat.seatNumber} (${item.metadata.reservedTicket.ticketedSeat.seatingType} class)`;
            } catch (e) {}  // eslint-disable-line no-empty

            let trainNumber = '';
            try {
                trainNumber = `${item.metadata.reservationFor.trainCompany.name} ${item.metadata.reservationFor.trainName} ${item.metadata.reservationFor.trainNumber}`;
            } catch (e) {}  // eslint-disable-line no-empty

            let boardingPass = '';
            try {
                boardingPass = item.metadata.reservedTicket.ticketToken;
            } catch (e) {}  // eslint-disable-line no-empty

            return {
                id: item.id,
                name: item.metadata.underName.name,
                reservationNumber: item.metadata.reservationNumber,
                trainNumber,
                from,
                to,
                boardingPass,
                seat,
                status: item.metadata.reservationStatus,
            };
        },
    },
    props: {
        items: Array,
    },
};
</script>
