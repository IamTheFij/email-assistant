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
                <v-list-tile v-for="(value, key) in menuItems" :to="{ name: 'Items', params: { type: key }}" :key="key">
                    <v-list-tile-action>
                      <v-icon>{{ value.icon }}</v-icon>
                    </v-list-tile-action>
                    <v-list-tile-content>
                        <v-list-tile-title>{{ key }}</v-list-tile-title>
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
import * as schemas from '@/components/schemas';

export default {
    data() {
        return {
            title: 'Email-assistant',
            menuItems: schemas.default,
        };
    },
    name: 'App',
};
</script>
