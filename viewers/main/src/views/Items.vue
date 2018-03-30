<template>
    <div v-if="isLoading">
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
    </div>
    <div v-else>
        <BusReservation :items="items" v-if="$route.params.type == 'BusReservation'"></BusReservation>
        <FlightReservation :items="items" v-else-if="$route.params.type == 'FlightReservation'"></FlightReservation>
        <ParcelDelivery :items="items" v-else-if="$route.params.type == 'ParcelDelivery'"></ParcelDelivery>
    </div>
</template>

<script>
import BusReservation from '@/components/BusReservation';
import FlightReservation from '@/components/FlightReservation';
import ParcelDelivery from '@/components/ParcelDelivery';

export default {
    components: {
        BusReservation,
        FlightReservation,
        ParcelDelivery,
    },
    created() {
        this.fetchItems();
    },
    watch: {
        $route: 'fetchItems',
    },
    data() {
        return {
            isLoading: false,
            items: [],
        };
    },
    methods: {
        fetchItems() {
            this.isLoading = true;
            fetch(`http://localhost:4100/token?filter_type=${this.$route.params.type}`)
                .then(r => r.json())
                .then((r) => {
                    this.isLoading = false;
                    this.items = r.tokens;
                });
        },
    },
};
</script>
