<template>
<v-container
  fluid
  style="min-height: 0;"
  grid-list-lg
  >
  <v-layout row wrap>
    <v-flex xs4 v-for="item in formattedItems">
      <v-card color="cyan darken-2" class="white--text">
        <v-container fluid grid-list-lg>
          <v-layout row>
            <v-flex xs7>
              <div>
                <div class="headline">
                  {{ item.organizationName }}
                  <template v-if="item.programName">
                    - {{ item.programName }}
                  </template>
                </div>
                <div>{{ item.memberName }}</div>
                <div>{{ item.membershipNumber }}</div>
              </div>
            </v-flex>
            <v-flex xs5 class="center">
              <img
                :src="item.image"
                height="125px"/>
            </v-flex>
          </v-layout>
        </v-container>
      </v-card>
    </v-flex>
  </v-layout>
</v-container>
</template>

<script>
export default {
    computed: {
        formattedItems() {
            return this.items.map(this.formatItem);
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
                    text: 'Organization name',
                    value: 'organizationName',
                },
                {
                    text: 'Program name',
                    value: 'programName',
                },
                {
                    text: 'Member name',
                    value: 'memberName',
                },
                {
                    text: 'Membership number',
                    value: 'membershipNumber',
                },
                {
                    text: 'Image',
                    value: 'image',
                },
            ],
        };
    },
    methods: {
        formatItem(item) {
            return {
                id: item.id,
                organizationName: item.metadata.hostingOrganization.name,
                programName: item.metadata.programName,
                memberName: item.metadata.member.name,
                membershipNumber: item.metadata.membershipNumber,
                image: item.metadata.image,
            };
        },
    },
    props: {
        items: Array,
    },
};
</script>

<style scoped>
img {
    max-height: 100%;
    max-width: 100%;
}

.center {
  text-align: center;
}
</style>
