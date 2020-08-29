from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from app.models import *
from app.calculations import *
from app.constants import *
import time

# Note- the code line numbers are for NEctroverse commit f7d73af2630f993fbe8c59fdaca31ad43e494543

class Command(BaseCommand): # must be called command, use file name to name the functionality
    @transaction.atomic # Makes it so all object saves get aggregated, otherwise process_tick would take a minute
    def handle(self, *args, **options):
        # docs say not to use print() but instead stdout
        self.stdout.write("=== Starting process_tick ===")

        ''' Whichever planet has Super stacker artifact increases in size by 7 per tick! not sure if it has to have been explored first to start or not
        for( a = 0 ; a < dbMapBInfoStatic[MAP_PLANETS] ; a++ )
        {
          dbMapRetrievePlanet( a, &planetd );
          if( (int)artefactPrecense( &planetd ) == 7 ){
            planetd.size += 7;
            dbMapSetPlanet( a, &planetd );
            break;
          }
        }
        '''

        # Loop through each user
        num_users_registered = 0 # im not actually using this anywhere yet
        for status in UserStatus.objects.all():
            start_t = time.time()
            self.stdout.write("User: " + status.user_name)
            self.stdout.write("id: " + str(status.user.id))

            num_users_registered += 1

            # Pull out race info for this user
            # Note, the below is just how to get the full field name in Django, not just 2 letter name
            # use {{ OBJNAME.get_FIELDNAME_display }} for templates
            # better not error out or someone was set to an invalid race somehow
            race_info = race_info_list[status.get_race_display()]


            '''
	        if( ( specopnum = dbUserSpecOpList( user->id, &specopd ) )  < 0 ) {
		        error( "Tick error: SpecOps User %d", user->id );
		        continue;
	        }
	        opvirus = 0;
	        /*
	        //WAR  ILLUSION we recalcul each tick
	        for(i=0;i<specopnum;i++) {
		        if (specopd[i].type == (CMD_SPELL_WARILLUSIONS | 0x1000)) {
			        fa = 0.4 + (1.2/255.0) * (float)( rand() & 255 );
			        nChicks = maind.totalunit[CMD_UNIT_WIZARD];
			        nIllusion = ( fa * cmdRace[maind.raceid].unit[CMD_UNIT_WIZARD] * (float)nChicks * ( 1.0 + 0.005*maind.totalresearch[CMD_RESEARCH_CULTURE] ) / cmdPsychicopDifficulty[CMD_SPELL_WARILLUSIONS] );
			        penalty = cmdGetOpPenalty( maind.totalresearch[CMD_RESEARCH_CULTURE], cmdPsychicopTech[CMD_SPELL_WARILLUSIONS] );
			        if( penalty )
		            	nIllusion = (float)nIllusion / ( 1.0 + 0.01*(float)penalty );
			        fa = 100.0 * (float)nIllusion / (float)maind.networth;
            			a = (int)( fa * 4.5 );
            			a += a * rand()%20;
            			if (a<0)
            				a = 0;
            			specopd[i].vars[0] = a;
		        } else if (specopd[i].type == (CMD_SPELL_DARKWEB | 0x1000)) {
			        fa = 0.4 + (1.2/255.0) * (float)( rand() & 255 );
			        nChicks = maind.totalunit[CMD_UNIT_WIZARD];
			        nIllusion = ( fa * cmdRace[maind.raceid].unit[CMD_UNIT_WIZARD] * (float)nChicks * ( 1.0 + 0.005*maind.totalresearch[CMD_RESEARCH_CULTURE] ) / cmdPsychicopDifficulty[CMD_SPELL_DARKWEB] );
			        penalty = cmdGetOpPenalty( maind.totalresearch[CMD_RESEARCH_CULTURE], cmdPsychicopTech[CMD_SPELL_DARKWEB] );
			        if( penalty )
			            	nIllusion = (float)nIllusion / ( 1.0 + 0.01*(float)penalty );
			        fa = 100.0 * (float)nIllusion / (float)maind.networth;
			        a = (int)( fa * 3.5 );
            			if (a<0)
            				a = 0;
            			specopd[i].vars[0] = a;
		        }
	        }
	        */
	        for( a = specopnum-1 ; a >= 0 ; a-- ) {
		        if( specopd[a].type == ( CMD_OPER_NETWORKVIRUS | 0x10000 ) )
			        opvirus++;
	        }
            '''


            # The block below goes through the construction list and reduces by 1 tick, and if 0 it builds it and creates the news entry
            # It might look messy listing them all out, but this is where the Building helper class "meets" the Model that gets stored in the db, I dont think theres a cleaner way to connect the two
            # lines 762 - 798 of cmdtick.c
            for job in Construction.objects.filter(user=status.user.id):
                job.ticks_remaining -= 1
                if job.ticks_remaining <= 0:
                    if job.building_type == 'SC':
                        job.planet.solar_collectors += job.n
                    if job.building_type == 'FR':
                        job.planet.fission_reactors += job.n
                    if job.building_type == 'MP':
                        job.planet.mineral_plants += job.n
                    if job.building_type == 'CL':
                        job.planet.crystal_labs += job.n
                    if job.building_type == 'RS':
                        job.planet.refinement_stations += job.n
                    if job.building_type == 'CT':
                        job.planet.cities += job.n
                    if job.building_type == 'RC':
                        job.planet.research_centers += job.n
                    if job.building_type == 'DS':
                        job.planet.defense_sats += job.n
                    if job.building_type == 'SN':
                        job.planet.shield_networks += job.n
                    if job.building_type == 'PL':
                        job.planet.portal = True
                        job.planet.portal_under_construction = False
                    job.planet.buildings_under_construction -= job.n
                    job.planet.save()

                    # TODO ADD IT TO THE NEWS!

                    job.delete()
                else:
                    job.save()

            # Repeat for units
            main_fleet = Fleet.objects.get(owner=status.user.id, main_fleet=True) # should only ever be 1
            for job in UnitConstruction.objects.filter(user=status.user.id):
                job.ticks_remaining -= 1
                if job.ticks_remaining <= 0:
                    setattr(main_fleet, job.unit_type, getattr(main_fleet, job.unit_type) + job.n)
                    main_fleet.save()
                    # TODO ADD IT TO THE NEWS!
                    job.delete()
                else:
                    job.save()






            ''' comes right before the planet loop
            nInfection = 0
            b = dbUserSpecOpList( usrid, &specopd );
            if( specopd ) {
	            for(a = 0; a < b; a++) {
		            if (specopd[a].type == (CMD_OPER_BIOINFECTION|0x10000)) {
			            nInfection++;
		            }
              	}
	            free( specopd );
            }
            '''

            # Loop through user's planets, lines 499 - 608 in cmdtick.c
            status.population = 0 # clear user's population
            status.num_planets = 0
            cmdTickProduction_solar = 0
            cmdTickProduction_fission = 0
            cmdTickProduction_mineral = 0
            cmdTickProduction_crystal = 0
            cmdTickProduction_ectrolium = 0
            cmdTickProduction_cities = 0
            cmdTickProduction_research = 0
            # Reset the building totals
            status.total_solar_collectors = 0
            status.total_fission_reactors = 0
            status.total_mineral_plants = 0
            status.total_crystal_labs = 0
            status.total_refinement_stations = 0
            status.total_cities = 0
            status.total_research_centers = 0
            status.total_defense_sats = 0
            status.total_shield_networks = 0
            status.total_portals = 0
            # Pull out x,y values of planets that have portals, for battlePortalCalc
            portal_xy_list = Planet.objects.filter(portal=True).values_list('x', 'y')
            start_t_planets = time.time()
            for planet in Planet.objects.filter(owner=status.user.id):
                status.num_planets += 1

                # Update Population
                planet.max_population = (planet.size * population_size_factor)
                planet.max_population += (planet.cities * building_production_cities)
                planet.max_population *= (1.00 + 0.01 * status.research_percent_population)

                #if (mainp->artefacts & ARTEFACT_32_BIT){
                #    planetd.maxpopulation *= 1.25;

                #ARTI CODE Super Stacker
                #	if(mainp->artefacts & ARTEFACT_*_BIT)
                #       planetd.maxpopulation = (float)( ( planetd.size * population_size_factor ) + ( planetd.building[CMD_BUILDING_CITIES] * (CMD_POPULATION_CITIES+1000) ) );
                #

                #if(mainp->artefacts & ARTEFACT_16_BIT) {
                #   planetd.population += ceil( (( planetd.population * ( race_info["pop_growth"] * 1.25 ) ) * ( 1.00 + 0.001 * status.research_percent_population )) * pow(0.75, (float)nInfection) );
                # else {
                #

                #if (mainp->artefacts &  ARTEFACT_512_BIT)
                #    planetd.current_population += ceil( (( 3 * planet.current_population * ( race_info["pop_growth"] ) ) * ( 1.00 + 0.001 * status.research_percent_population )) * pow(0.75, (float)nInfection) );
                #else
                nInfection = 0
                planet.current_population += int(np.ceil(planet.current_population * race_info["pop_growth"] * (1.00 + 0.01 * status.research_percent_population) * 0.75**nInfection))
                planet.current_population = min(planet.max_population, planet.current_population)


                if planet.portal:
                    planet.protection = 100
                else:
	                planet.protection = int(100.0 * battlePortalCalc(planet.x, planet.y, portal_xy_list, status.research_percent_culture))

                # Add planet pop to total pop
                status.population += planet.current_population

                # Add buildings to running total for player
                status.total_solar_collectors += planet.solar_collectors
                status.total_fission_reactors += planet.fission_reactors
                status.total_mineral_plants += planet.mineral_plants
                status.total_crystal_labs += planet.crystal_labs
                status.total_refinement_stations += planet.refinement_stations
                status.total_cities += planet.cities
                status.total_research_centers += planet.research_centers
                status.total_defense_sats += planet.defense_sats
                status.total_shield_networks += planet.shield_networks
                status.total_portals += int(planet.portal)

                # Calc total buildings on this planet (not player total)
                planet.total_buildings = planet.solar_collectors + planet.fission_reactors + planet.mineral_plants + planet.crystal_labs + planet.refinement_stations + planet.cities + planet.research_centers + planet.defense_sats + planet.shield_networks + int(planet.portal)

                # Multiply number of buildings by the resource they generate and apply planet bonus
                factor = 1.0
                #if ( mainp->artefacts & ARTEFACT_2_BIT)
                #	factor = 2.0
                cmdTickProduction_solar += (building_production_solar * planet.solar_collectors) * (1 + factor*planet.bonus_solar/100.0)
                cmdTickProduction_fission += building_production_fission * planet.fission_reactors
                cmdTickProduction_mineral += (building_production_mineral * planet.mineral_plants) * (1 + factor*planet.bonus_mineral/100.0)
                cmdTickProduction_crystal += (building_production_crystal * planet.crystal_labs) * (1 + factor*planet.bonus_crystal/100.0)
                cmdTickProduction_ectrolium += (building_production_ectrolium * planet.refinement_stations) * (1 + factor*planet.bonus_ectrolium/100.0)
                cmdTickProduction_cities += building_production_cities * planet.cities
                cmdTickProduction_research += building_production_research * planet.research_centers

                #for( b = 0 ; b < CMD_UNIT_NUMUSED ; b++ )
                #    StationedUnits[b] += planetd.unit[b];

                #if( ( b = (int)artefactPrecense( &planetd ) ) < 0 )
                #    continue;

                #if( dbEmpireGetInfo( mainp->empire, &empired ) < 0 )
                #    continue;

                #empired.artefacts |= 1 << b;
                #dbEmpireSetInfo( mainp->empire, &empired );

                # Update overbuilt factor
                planet.overbuilt = calc_overbuild(planet.size, planet.total_buildings + planet.buildings_under_construction)
                planet.overbuilt_percent = (planet.overbuilt-1.0)*100 # came from html_gameplay.c line 5541
                # The above isnt even the correct formula im pretty sure

                planet.save()

            print("Planet loop took", time.time() - start_t_planets, "seconds")

            # Calc total buildings for user
            status.total_buildings = status.total_solar_collectors + status.total_fission_reactors + status.total_mineral_plants + status.total_crystal_labs + status.total_refinement_stations + status.total_cities + status.total_research_centers + status.total_defense_sats + status.total_shield_networks + status.total_portals



            ####################
            # Research Related #
            ####################
            #lines 811 - 908 of cmdtick.c

            #if( maind.artefacts & ARTEFACT_16_BIT )
            #   artiBonus = maind.totalbuilding[CMD_BUILDING_FISSION] * 100;*/


            # The arti code lines below were inside "for research in research-type" loop, i pulled them out bcause im not doing it in a loop
            #if(maind.artefacts & ARTEFACT_64_BIT)
            #	fa = ( status.alloc_research_culture * ( 100 * cmdTickProduction[CMD_BUILDING_RESEARCH] * 1.20 + maind.fundresearch + artiBonus) ) / 10000.0;
            # ARTI CODE Foohon Ancestry
            #       if(maind.artefacts & ARTEFACT_*_BIT)
            #	        fa += ( status.alloc_research_culture * (double)maind.ressource[CMD_RESSOURCE_POPULATION] ) / ( 400.0 * 100.0 );
            #

            # This is the research POINTS part
            CMD_ENLIGHT_RESEARCH = 0 # this is really a value of an enum
            artiBonus = 0
            # FIXME obviously figure out how to clean up this
            status.research_points_military += race_info["research_bonus_military"] * status.alloc_research_military * (100*cmdTickProduction_research + 1.2*status.current_research_funding + artiBonus)  / 10000.0 * specopEnlightemntCalc(status.user.id, CMD_ENLIGHT_RESEARCH) + int(race_info["race_special"] == "RACE_SPECIAL_POPRESEARCH")*1.2*(status.alloc_research_military * status.population)/(600.0*100.0)
            status.research_points_construction += race_info["research_bonus_construction"] * status.alloc_research_construction * (100*cmdTickProduction_research + 1.2*status.current_research_funding + artiBonus)  / 10000.0 * specopEnlightemntCalc(status.user.id, CMD_ENLIGHT_RESEARCH) + int(race_info["race_special"] == "RACE_SPECIAL_POPRESEARCH")*1.2*(status.alloc_research_construction * status.population)/(600.0*100.0)
            status.research_points_tech += race_info["research_bonus_tech"] * status.alloc_research_tech * (100*cmdTickProduction_research + 1.2*status.current_research_funding + artiBonus)  / 10000.0 * specopEnlightemntCalc(status.user.id, CMD_ENLIGHT_RESEARCH) + int(race_info["race_special"] == "RACE_SPECIAL_POPRESEARCH")*1.2*(status.alloc_research_tech * status.population)/(600.0*100.0)
            status.research_points_energy += race_info["research_bonus_energy"] * status.alloc_research_energy * (100*cmdTickProduction_research + 1.2*status.current_research_funding + artiBonus)  / 10000.0 * specopEnlightemntCalc(status.user.id, CMD_ENLIGHT_RESEARCH) + int(race_info["race_special"] == "RACE_SPECIAL_POPRESEARCH")*1.2*(status.alloc_research_energy * status.population)/(600.0*100.0)
            status.research_points_population += race_info["research_bonus_population"] * status.alloc_research_population * (100*cmdTickProduction_research + 1.2*status.current_research_funding + artiBonus)  / 10000.0 * specopEnlightemntCalc(status.user.id, CMD_ENLIGHT_RESEARCH) + int(race_info["race_special"] == "RACE_SPECIAL_POPRESEARCH")*1.2*(status.alloc_research_population * status.population)/(600.0*100.0)
            status.research_points_culture += race_info["research_bonus_culture"] * status.alloc_research_culture * (100*cmdTickProduction_research + 1.2*status.current_research_funding + artiBonus)  / 10000.0 * specopEnlightemntCalc(status.user.id, CMD_ENLIGHT_RESEARCH) + int(race_info["race_special"] == "RACE_SPECIAL_POPRESEARCH")*1.2*(status.alloc_research_culture * status.population)/(600.0*100.0)
            status.research_points_operations += race_info["research_bonus_operations"] * status.alloc_research_operations * (100*cmdTickProduction_research + 1.2*status.current_research_funding + artiBonus)  / 10000.0 * specopEnlightemntCalc(status.user.id, CMD_ENLIGHT_RESEARCH) + int(race_info["race_special"] == "RACE_SPECIAL_POPRESEARCH")*1.2*(status.alloc_research_operations * status.population)/(600.0*100.0)

            # Make sure none of the research points are negative (might be able to have this automatically done with a model attribute)
            status.research_points_military     = max(0.0, status.research_points_military)
            status.research_points_construction = max(0.0, status.research_points_construction)
            status.research_points_tech         = max(0.0, status.research_points_tech)
            status.research_points_energy       = max(0.0, status.research_points_energy)
            status.research_points_population   = max(0.0, status.research_points_population)
            status.research_points_culture      = max(0.0, status.research_points_culture)
            status.research_points_operations   = max(0.0, status.research_points_operations)

            # Research funding decay
            status.current_research_funding = max(0.0, (0.9 * status.current_research_funding))


            # Next is the research PERCENTAGE part

            # SK: because of the network backbone arti, we need to calculate Tech research first
            # addedFromTech = 0 NOTE THAT THIS VALUE GETS ADDED BY ALL RESEARCH TYPES EXCEPT TECH
            # The part below went inside the for loop
            # put this arti last, you need the other ones calculated before this one.
            #   //ARTI CODE network backbone
            #if(maind.artefacts & ARTEFACT_*_BIT)
            #{
            #   // exclude tech research from having this bonus (otherwise there is no cap)
            #   if( a != CMD_RESEARCH_TECH)
            #       {
            #        fa += addedFromTech;
            #       }
            #}*/

            # CODE_ARTI
            # evo obelisk
            #if( ( maind.artefacts & ARTEFACT_64_BIT )){//& ( ( a == CMD_RESEARCH_ENERGY ) || ( a == CMD_RESEARCH_MILITARY ) ) ) {
            #    fa += 20.0;
            #}

            #ARTEFACT_64_BIT
            #if( ( maind.artefacts & ARTEFACT_4_BIT ) && a == CMD_RESEARCH_MILITARY){//& ( ( a == CMD_RESEARCH_ENERGY ) || ( a == CMD_RESEARCH_MILITARY ) ) ) {
            #    fa += 30.0;
            #}*/

            #if (( maind.artefacts & ARTEFACT_16_BIT ) && a == CMD_RESEARCH_CULTURE): # & ( ( a == CMD_RESEARCH_ENERGY ) || ( a == CMD_RESEARCH_MILITARY ) ) ) {
            #    fa += 50.0

            # Target is a function of research points and NW
            # Goes up or down by 1 each tick to reach target slowly
            # Note that it uses the last ticks NW for whatever reason
            status.research_percent_military     += np.sign(race_info.get("research_max_military", 200) * (1.0 - np.exp(status.research_points_military / (-10.0 * status.networth)))) # np.sign returns a 1 or -1
            status.research_percent_construction += np.sign(race_info.get("research_max_construction", 200) * (1.0 - np.exp(status.research_points_construction / (-10.0 * status.networth))))
            status.research_percent_tech         += np.sign(race_info.get("research_max_tech", 200) * (1.0 - np.exp(status.research_points_tech / (-10.0 * status.networth))))
            status.research_percent_energy       += np.sign(race_info.get("research_max_energy", 200) * (1.0 - np.exp(status.research_points_energy / (-10.0 * status.networth))))
            status.research_percent_population   += np.sign(race_info.get("research_max_population", 200) * (1.0 - np.exp(status.research_points_population / (-10.0 * status.networth))))
            status.research_percent_culture      += np.sign(race_info.get("research_max_culture", 200) * (1.0 - np.exp(status.research_points_culture / (-10.0 * status.networth))))
            status.research_percent_operations   += np.sign(race_info.get("research_max_operations", 200) * (1.0 - np.exp(status.research_points_operations / (-10.0 * status.networth))))







            #####################
            # Energy Production #
            #####################

            # calc infos
            fa = cmdTickProduction_solar / specopSolarCalc(status.user.id)
            if (race_info["race_special"] == 'RACE_SPECIAL_SOLARP15'):
	            fa *= 1.15

            #ARTI CODE Ether Palace
            #if( maind.artefacts & ARTEFACT_32_BIT ) {
            # 	fa *= 1.30;

            fb = cmdTickProduction_fission

            #if( maind.artefacts & ARTEFACT_32_BIT ) {
                #fb *= 1.20;

            fa += fb

            #ARTI CODE Ether Garden
            #if(maind.artefacts & ARTEFACT_ETHER_BIT) {
	        #    fa *= 1.10;
            #}

            #if(maind.artefacts & ARTEFACT_8_BIT) {
            #   fa *= 0.9;

            #ARTI CODE Ether Palace
            #if(maind.artefacts & ARTEFACT_8_BIT) {
            #   fa *= 1.25;

            # Enlightenment
            CMD_ENLIGHT_ENERGY = 0
            fa *= specopEnlightemntCalc(status.user.id, CMD_ENLIGHT_ENERGY)
            fb = race_info.get("energy_production", 1.0) * (1.00 + 0.01*status.research_percent_energy)
            status.energy_production = fa * fb


            fc = stockpile * status.energy_production
            fa = energy_decay_factor
            #if(maind.artefacts & ARTEFACT_8_BIT) {
            #    fa /= 2.0;
            #}
            status.energy_decay = fa * max(0.0, status.energy - fc)



            ####################
            # Buildings Upkeep #
            ####################
            # lines 966 - 976
            status.buildings_upkeep = \
                status.total_solar_collectors * upkeep_solar_collectors * fb +\
                status.total_fission_reactors * upkeep_fission_reactors * fb +\
                status.total_mineral_plants * upkeep_mineral_plants +\
                status.total_crystal_labs * upkeep_crystal_labs +\
                status.total_refinement_stations * upkeep_refinement_stations +\
                status.total_cities * upkeep_cities +\
                status.total_research_centers * upkeep_research_centers +\
                status.total_defense_sats * upkeep_defense_sats +\
                status.total_shield_networks * upkeep_shield_networks




            # THIS IS WHERE I LEFT OFF




            opvirus = 0

            ################
            # Units Upkeep #
            ################
            status.units_upkeep = 0



            ############################
            # production/upkeep/income #
            ############################
            # line 1025-1077 of cmdtick.c

            #ARTI CODE Romulan Military Outpost
            #if(maind.artefacts & ARTEFACT_16_BIT) {
            #   maind.infos[INFOS_UNITS_UPKEEP] *= 1.15;

            #ARTEFACT_2_BIT check for the timer!
            #int artiUpkeepReduction = dbCheckArtifactTimer(maind.empire, 10);
            #    if (artiUpkeepReduction > 0){
            #        maind.infos[INFOS_UNITS_UPKEEP] *= pow(0.9,(double)artiUpkeepReduction);


            status.population_upkeep_reduction = (1.0/35.0) * status.population
            #Population Reduction changed to include portals + units
            status.portals_upkeep = max(0.0, (status.total_portals - 1)**1.2736 * 10000.0 / (1.0 + status.research_percent_culture/100.0))
            status.population_upkeep_reduction = min(status.population_upkeep_reduction, (status.buildings_upkeep + status.units_upkeep + status.portals_upkeep))


            # Network Virus Effect.
            for a in range(opvirus):
                #status.population_upkeep_reduction -= fmax( 0.0, ( status.population_upkeep_reduction * 0.05 ) );
                status.buildings_upkeep *=  1.15

            CMD_ENLIGHT_CRY = 0 # its actually a specific value of an enumeration, see enum.h
            CMD_ENLIGHT_MINERAL = 0
            CMD_ENLIGHT_ECTRO = 0
            status.crystal_production = (race_info.get("crystal_production", 1.0) * cmdTickProduction_crystal) * specopEnlightemntCalc(status.user.id, CMD_ENLIGHT_CRY)

            # ARTI CODE Crystalline Entity | reduces crystal decay by 75%
            #	if(maind.artefacts & ARTEFACT_*_BIT)
            #	fa /= 4;
            fa = crystal_decay_factor
            #if(maind.artefacts & ARTEFACT_8_BIT) {
            #	fa /= 2.0;
            #}
            status.crystal_decay = fa * max(0.0, (status.crystals - (settings_num_value * status.crystal_production)))


            #ARTI CODE Mana Gate
                #if(maind.artefacts & ARTEFACT_MANA_BIT)
                #	status.portals_upkeep /= 2;

            status.mineral_production = (race_info.get("mineral_production", 1.0) * cmdTickProduction_mineral ) * specopEnlightemntCalc(status.user.id, CMD_ENLIGHT_MINERAL);
            status.ectrolium_production = (race_info.get("ectrolium_production", 1.0) * cmdTickProduction_ectrolium ) * specopEnlightemntCalc(status.user.id, CMD_ENLIGHT_ECTRO);

            #if(maind.artefacts & ARTEFACT_64_BIT)
            #    status.mineral_production *= 1.15

            ''' tax stuff that i probably wont include (lines are also commented below in the budget calculations)
            maind.infos[INFOS_ENERGY_TAX] = fmax( 0.0, ( maind.infos[INFOS_ENERGY_PRODUCTION] * empired.taxation ) );
            maind.infos[INFOS_MINERAL_TAX] = fmax( 0.0, ( maind.infos[INFOS_MINERAL_PRODUCTION] * empired.taxation ) );
            maind.infos[INFOS_CRYSTAL_TAX] = fmax( 0.0, ( maind.infos[INFOS_CRYSTAL_PRODUCTION] * empired.taxation ) );
            maind.infos[INFOS_ECTROLIUM_TAX] = fmax( 0.0, ( maind.infos[INFOS_ECTROLIUM_PRODUCTION] * empired.taxation ) );
            '''
            status.energy_income = status.energy_production - status.energy_decay - status.buildings_upkeep - status.units_upkeep + status.population_upkeep_reduction - status.portals_upkeep # - maind.infos[INFOS_ENERGY_TAX];
            status.mineral_income = status.mineral_production #(status.mineral_production - maind.infos[INFOS_MINERAL_TAX]);
            status.crystal_income = status.crystal_production - status.crystal_decay # ((status.crystal_production - maind.infos[INFOS_CRYSTAL_TAX] ) - status.crystal_decay);
            status.ectrolium_income = status.ectrolium_production # (status.ectrolium_production - maind.infos[INFOS_ECTROLIUM_TAX]);




            ###############
            # Fleet Stuff #
            ###############
            # TODO ONCE MODELS ARE CREATED



            #############################
            # Interest and Income Given #
            #############################
            # line 1224 - 1247
            '''
            if (race_info["race_special"] == 'RACE_SPECIAL_WOOKIEE'):
	            status.energy_interest    = min(0.005 * status.energy,    status.energy_production)
	            status.mineral_interest   = min(0.005 * status.mineral,   status.mineral_production)
	            status.crystal_interest   = min(0.005 * status.crystal,   status.crystal_production)
	            status.ectrolium_interest = min(0.005 * status.ectrolium, status.ectrolium_production)

	            status.energy_income    += maind.infos[INFOS_ENERGY_INTEREST];
	            status.mineral_income   += maind.infos[INFOS_MINERAL_INTEREST];
	            status.crystal_income   += maind.infos[INFOS_CRYSTAL_INTEREST];
	            status.ectrolium_income += maind.infos[INFOS_ECTROLIUM_INTEREST];
            else:
            '''
            status.energy_interest = 0
            status.mineral_interest = 0
            status.crystal_interest = 0
            status.ectrolium_interest = 0

            # Give user the final income FIXME might be able to keep it a non-negative number using model attribute
            status.energy    = max(0.0, status.energy    + status.energy_income)
            status.minerals  = max(0.0, status.minerals  + status.mineral_income)
            status.crystals  = max(0.0, status.crystals  + status.crystal_income)
            status.ectrolium = max(0.0, status.ectrolium + status.ectrolium_income)



            ###########################
            # Networth and unit decay #
            ###########################
            # lines 1250 - 1330
	        #fa = 0;
	        #fb = 3

	        # Clear networth
            status.networth = 0

            for planet in Planet.objects.filter(owner=status.user.id):
                '''
                e = 0
                if( planetd.unit[CMD_UNIT_PHANTOM] ) {
                    planetd.unit[CMD_UNIT_PHANTOM] -= (int)ceil( phdecay * (float)(planetd.unit[CMD_UNIT_PHANTOM]) );
                    e |= 1;
                }
                for( c = b ; c >= 0 ; c-- ) {
                    d = (int)ceil( (float)planetd.unit[c] * 0.02 );
                    planetd.unit[c] -= d;
                    maind.totalunit[c] -= d;
                    e |= d;
                }
                if( e ) {
                    dbMapSetPlanet( plist[a], &planetd );
                }
                '''
                # Networth Segment
                status.networth += (planet.bonus_solar * 1.25)
                status.networth += (planet.bonus_mineral * 1.45)
                status.networth += (planet.bonus_crystal * 2.25)
                status.networth += (planet.bonus_ectrolium * 1.65)
                status.networth += (planet.bonus_fission * 5.0)

                # I DIDNT ADD MEGA FLAG YET
                #if( planetd.flags & CMD_PLANET_FLAGS_MEGA ) {
                #    fa += planetd.size;
                #    fb++;
                #} else {
                status.networth += (planet.size * 1.75)
                #}

            #if fa: THIS ONLY HAPPENS WHEN ITS A MEGA PLANET
            #    maind.networth += (fa * fb)


            '''
            for( a = 0 ; a < CMD_UNIT_NUMUSED ; a++ ) {
	            status.networth += maind.totalunit[a] * cmdUnitStats[a][CMD_UNIT_STATS_NETWORTH];
            }
            '''
            # Since its the same constant for nw per building, this could be simplified into status.total_buildings * nw-per-building
            status.networth += status.total_solar_collectors * networth_per_building
            #if( maind.artefacts & ARTEFACT_16_BIT && a == CMD_BUILDING_FISSION)
	        #    continue;
            #else
            status.networth += status.total_fission_reactors * networth_per_building
            status.networth += status.total_mineral_plants * networth_per_building
            status.networth += status.total_crystal_labs * networth_per_building
            status.networth += status.total_refinement_stations * networth_per_building
            status.networth += status.total_cities * networth_per_building
            status.networth += status.total_research_centers * networth_per_building
            status.networth += status.total_defense_sats * networth_per_building
            status.networth += status.total_shield_networks * networth_per_building

            status.networth += (0.005 * status.population)

            status.networth += (0.001 * status.research_points_military)
            status.networth += (0.001 * status.research_points_construction)
            status.networth += (0.001 * status.research_points_tech)
            status.networth += (0.001 * status.research_points_energy)
            status.networth += (0.001 * status.research_points_population)
            status.networth += (0.001 * status.research_points_culture)
            status.networth += (0.001 * status.research_points_operations)

            ###############
            # Special Ops #
            ###############

            # TODO


            ################
            # Market Decay #
            ################

            # TODO

            # Save objects to database
            status.save()

            print("Seconds taken to process user:", time.time() - start_t)

        self.stdout.write("=== Ending process_tick ===")
