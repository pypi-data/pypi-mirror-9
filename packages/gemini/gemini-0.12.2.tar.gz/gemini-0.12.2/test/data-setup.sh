gemini load --skip-gene-tables --test-mode --skip-gerp --skip-cadd -v test.multiple-alts.decomp.snpeff.vcf -t snpEff test.mad.db
gemini load --skip-gene-tables --test-mode -v test.cosmic.vcf --skip-gerp-bp --skip-cadd test.cosmic.db
gemini load --skip-gene-tables --test-mode -v test.roh.vcf --skip-gerp-bp --skip-cadd -t snpEff test.roh.vcf.db
gemini load --skip-gene-tables --test-mode -v test.cadd.vcf --skip-gerp-bp --skip-cadd test.no.cadd.db
gemini load --skip-gene-tables --test-mode -v test.snpeff.vcf --skip-gerp-bp --skip-cadd -t snpEff test.snpeff.vcf.db
gemini load --skip-gene-tables --test-mode -v test1.snpeff.vcf --skip-gerp-bp --skip-cadd -t snpEff test1.snpeff.db
gemini load --skip-gene-tables --test-mode -v test1.snpeff.vcf --skip-gerp-bp --skip-cadd -t VEP test1.vep.db
gemini load --skip-gene-tables --test-mode -v test2.snpeff.vcf --skip-gerp-bp --skip-cadd test2.snpeff.db
gemini load --skip-gene-tables --test-mode -v test3.snpeff.vcf --skip-gerp-bp --skip-cadd test3.snpeff.db
gemini load --skip-gene-tables --test-mode -v test.clinvar.vcf --skip-gerp-bp --skip-cadd test.clinvar.db
gemini load --skip-gene-tables --test-mode -v test4.vep.snpeff.vcf --skip-gerp-bp --skip-cadd -t snpEff test4.snpeff.db
gemini load --skip-gene-tables --test-mode -v test4.vep.snpeff.vcf --skip-gerp-bp --skip-cadd -t VEP test4.vep.db
gemini load --skip-gene-tables --test-mode -v test5.vep.snpeff.vcf --skip-gerp-bp --skip-cadd -t snpEff test5.snpeff.db
gemini load --skip-gene-tables --test-mode -v test5.vep.snpeff.vcf --skip-gerp-bp --skip-cadd -t VEP test5.vep.db
gemini load --test-mode -v test.query.vcf --skip-gerp-bp --skip-cadd -t snpEff test.query.db
gemini load --skip-gene-tables --test-mode -v test.query.vcf --skip-gerp-bp --skip-cadd -t VEP test.query.vep.db
gemini load --test-mode -v test.query.vcf --skip-gerp-bp --skip-cadd --cores 2 -t snpEff test.query.core.db
gemini load --skip-gene-tables --test-mode -v test.region.vep.vcf --skip-gerp-bp --skip-cadd -t VEP test.region.db
gemini load --skip-gene-tables --test-mode -v test.burden.vcf --skip-gerp-bp --skip-cadd -t VEP -p test.burden.ped test.burden.db
gemini load --skip-gene-tables --test-mode -v test.comp_het.vcf --skip-gerp-bp --skip-cadd -t snpEff -p test.comp_het.ped test.comp_het.db
gemini load --skip-gene-tables --test-mode -v test.comp_het.2.vcf --skip-gerp-bp --skip-cadd -t snpEff test.comp_het_default.db
gemini load --skip-gene-tables --test-mode -v test.comp_het.3.vcf --skip-gerp-bp --skip-cadd -t snpEff -p test.comp_het.ped test.comp_het_default.2.db
gemini load --skip-gene-tables --test-mode -v test.comp_het.4.vcf --skip-gerp-bp --skip-cadd -t snpEff -p test.comp_het.2.ped test.comp_het_default.4.db
gemini load --skip-gene-tables --test-mode -v test.comp_het.5.vcf --skip-gerp-bp --skip-cadd -t snpEff -p test.comp_het.2.ped test.comp_het_default.5.db
gemini load --skip-gene-tables --test-mode -v test.comp_het.6.vcf --skip-gerp-bp --skip-cadd -t snpEff -p test.comp_het.2.ped test.comp_het_default.6.db
gemini load --skip-gene-tables --test-mode -v test.comp_het.7.vcf --skip-gerp-bp --skip-cadd -t snpEff -p test.comp_het.2.ped test.comp_het_default.7.db
gemini load --skip-gene-tables --test-mode -v test.auto_dom.vcf --skip-gerp-bp --skip-cadd -t snpEff -p test.auto_dom.ped test.auto_dom.db
gemini load --skip-gene-tables --test-mode -v test.auto_dom.no_parents.vcf --skip-gerp-bp --skip-cadd -t snpEff -p test.auto_dom.no_parents.ped test.auto_dom.no_parents.db
gemini load --skip-gene-tables --test-mode -v test.auto_dom.no_parents.2.vcf --skip-gerp-bp --skip-cadd -t snpEff -p test.auto_dom.no_parents.2.ped test.auto_dom.no_parents.2.db
gemini load --skip-gene-tables --test-mode -v test.auto_dom.no_parents.3.vcf --skip-gerp-bp --skip-cadd -t snpEff -p test.auto_dom.no_parents.3.ped test.auto_dom.no_parents.3.db
gemini load --skip-gene-tables --test-mode -v test.auto_dom.no_parents.4.vcf --skip-gerp-bp --skip-cadd -t snpEff -p test.auto_dom.no_parents.4.ped test.auto_dom.no_parents.4.db
gemini load --skip-gene-tables --test-mode -v test.auto_dom.no_parents.5.vcf --skip-gerp-bp --skip-cadd -t snpEff -p test.auto_dom.no_parents.5.ped test.auto_dom.no_parents.5.db
gemini load --skip-gene-tables --test-mode -v test.auto_rec.vcf --skip-gerp-bp --skip-cadd -t snpEff -p test.auto_rec.ped test.auto_rec.db
gemini load --skip-gene-tables --test-mode -v test.auto_rec.no_parents.vcf --skip-gerp-bp --skip-cadd -t snpEff -p test.auto_rec.no_parents.ped test.auto_rec.no_parents.db
gemini load --skip-gene-tables --test-mode -v test.auto_rec.no_parents.2.vcf --skip-gerp-bp --skip-cadd -t snpEff -p test.auto_rec.no_parents.2.ped test.auto_rec.no_parents.2.db
gemini load --skip-gene-tables --test-mode -v test.auto_rec.no_parents.3.vcf --skip-gerp-bp --skip-cadd -t snpEff -p test.auto_rec.no_parents.3.ped test.auto_rec.no_parents.3.db
gemini load --skip-gene-tables --test-mode -v test.auto_rec.no_parents.4.vcf --skip-gerp-bp --skip-cadd -t snpEff -p test.auto_rec.no_parents.4.ped test.auto_rec.no_parents.4.db
gemini load --skip-gene-tables --test-mode -v test.auto_rec.no_parents.5.vcf --skip-gerp-bp --skip-cadd -t snpEff -p test.auto_rec.no_parents.5.ped test.auto_rec.no_parents.5.db
gemini load --skip-gene-tables --test-mode -v test.de_novo.vcf --skip-gerp-bp --skip-cadd -t snpEff -p test.de_novo.ped test.de_novo.db
gemini load --skip-gene-tables --test-mode -v test.de_novo.affected.and.unaffected.vcf --skip-gerp-bp --skip-cadd -t snpEff -p test.de_novo.affected.and.unaffected.ped test.de_novo.affected.and.unaffected.db
gemini load --skip-gene-tables --test-mode -p test4.snpeff.ped -v test4.vep.snpeff.vcf --skip-gerp-bp --skip-cadd -t snpEff test4.snpeff.ped.db
gemini load --skip-gene-tables --test-mode -v test.vcf_id.snpeff.vcf  --skip-gerp-bp --skip-cadd -t snpEff test.vcf_id.snpeff.vcf.db
gemini load --skip-gene-tables --test-mode -p test.de_novo.ped -v test.family.vcf  --skip-gerp-bp --skip-cadd -t snpEff test.family.db
gemini load --skip-gene-tables --test-mode -p test_extended_ped.ped -v test4.vep.snpeff.vcf  --skip-gerp-bp --skip-cadd -t snpEff extended_ped.db
cp extended_ped.db test.amend.db
gemini load -p test.somatic.ped -v test.somatic.vcf  --skip-gerp-bp --skip-cadd -t VEP test.somatic.db
gemini load -p test.fusions.ped -v test.fusions.vcf  --skip-gerp-bp --skip-cadd -t VEP test.fusions.db
gemini load --skip-gene-tables --test-mode -v test.exac.vcf --skip-gerp-bp --skip-cadd test.exac.db
