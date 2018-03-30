<template>
    <v-app>
        <v-navigation-drawer
            fixed
            app
            >
            <v-list dense>
                <v-list-tile :to="{ name: 'Home' }" exact>
                    <v-list-tile-action>
                        <v-icon>home</v-icon>
                    </v-list-tile-action>
                    <v-list-tile-content>
                        <v-list-tile-title>Home</v-list-tile-title>
                    </v-list-tile-content>
                </v-list-tile>
                <v-list-tile :to="{ name: 'Items', params: { type: 'ParcelDelivery' }}">
                    <v-list-tile-action>
                        <v-icon>local_post_office</v-icon>
                    </v-list-tile-action>
                    <v-list-tile-content>
                        <v-list-tile-title>Parcel deliveries</v-list-tile-title>
                    </v-list-tile-content>
                </v-list-tile>
                <v-list-tile :to="{ name: 'Items', params: { type: 'BusReservation' }}">
                    <v-list-tile-action>
                        <v-icon>directions_bus</v-icon>
                    </v-list-tile-action>
                    <v-list-tile-content>
                        <v-list-tile-title>Bus reservations</v-list-tile-title>
                    </v-list-tile-content>
                </v-list-tile>
                <v-list-tile :to="{ name: 'Items', params: { type: 'FlightReservation' }}">
                    <v-list-tile-action>
                        <v-icon>flight</v-icon>
                    </v-list-tile-action>
                    <v-list-tile-content>
                        <v-list-tile-title>Flight reservations</v-list-tile-title>
                    </v-list-tile-content>
                </v-list-tile>
            </v-list>
        </v-navigation-drawer>
        <v-toolbar
            app
            >
            <v-toolbar-title v-text="title"></v-toolbar-title>
        </v-toolbar>
        <v-content>
            <router-view/>
        </v-content>
    </v-app>
</template>

<script>
export default {
    data() {
        return {
            title: 'Email-assistant',
        };
    },
    name: 'App',
};
</script>
